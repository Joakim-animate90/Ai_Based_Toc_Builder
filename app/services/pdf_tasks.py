from app.repository.open_ai_db import OpenAIDB
from app.services.toc_service import TOCService


def process_pdf_task(ticket_id: str):
    db = OpenAIDB()
    record = db.get(ticket_id)
    if not record or not record.get("payload"):
        db.update_status_and_result(ticket_id, "failed", {"error": "No payload found"})
        return

    try:
        payload = record["payload"]
        filename = payload.get("filename")
        pdf_content_hex = payload.get("pdf_content")
        max_pages = payload.get("max_pages", 5)

        if not filename or not pdf_content_hex:
            db.update_status_and_result(
                ticket_id,
                "failed",
                {"error": "Missing filename or pdf_content in payload"},
            )
            return

        pdf_content = bytes.fromhex(pdf_content_hex)
        toc_service = TOCService()
        print(
            "--------------------------- Extracting  Toc From Pdf --------------------------------------"
        )
        toc_content, output_file = toc_service.extract_toc_from_upload(
            pdf_content, filename, None, max_pages
        )
        print(
            "---------------------------- Finish Extracting Toc ------------------------------"
        )
        result = {
            "message": "TOC extraction completed",
            "toc_content": toc_content,
            "output_file": output_file,
        }
        db.update_status_and_result(ticket_id, "completed", result)
        return result
    except Exception as e:
        db.update_status_and_result(ticket_id, "failed", {"error": str(e)})
        return {"error": str(e)}

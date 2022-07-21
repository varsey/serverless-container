import os
import imaplib
import eml_parser
from .Processor import Processor


class ProcessorServer(Processor):
    # EMAIL MESSAGE
    def get_message_attributes(self, data):

        def _parsing_wrapper(attachment_path):
            full_text = ''
            docx_file = ''.join(attachment_path.split('.')[:-1]) + self.docx_ext
            csv_file = ''.join(attachment_path.split('.')[:-1]) + '.csv'
            if os.path.isfile(docx_file):
                full_text = self.parse_docx(docx_file)
            elif os.path.isfile(csv_file):
                full_text = self.parse_csv(csv_file)
            else:
                self.log.error('No files to process!')
            return full_text

        ep = eml_parser.EmlParser(include_raw_body=True, include_attachment_data=True)
        email, message_text, header_from = '', '', ''
        att_text, attach_name, attach_names, full_texts, attach_texts = '', '', [], [], {}
        for response_part in data:
            if isinstance(response_part, tuple):
                parsed_eml = ep.decode_email_bytes(response_part[1])
                message_text, header_from = self.get_message_text(parsed_eml)
                attach_names = self.save_attachments_files(parsed_eml)
                for attach_name in attach_names:
                    try:
                        attachment_path = self.convert_attachment_file(attach_name)
                        full_text = _parsing_wrapper(attachment_path)
                        attach_texts[attach_name] = full_text
                    except Exception as ex:
                        self.worker.error_processor(ex)
                        continue
        return attach_texts, message_text, header_from

    # EMAIL MESSAGE FROM GMAIL
    def process_email(self):
        result = []
        email, password, server = os.getenv("EMAIL"), os.getenv('PASS'), os.getenv('SERVER')

        mail = imaplib.IMAP4_SSL(server)
        mail.login(email, password)
        mail.select('inbox')

        status, data = mail.search(None, 'ALL')

        mail_ids = []
        for block in data:
            mail_ids += block.split()

        for i in mail_ids[-1:]:
            try:
                status, data = mail.fetch(i, '(BODY.PEEK[])')
                attach_texts, message_text, header_from = self.get_message_attributes(data)
                result = self.file_parsing(message_text, attach_texts, header_from)
            except Exception as ex:
                self.worker.error_processor(ex)
                self.log.warning('email processing failed')

        return result

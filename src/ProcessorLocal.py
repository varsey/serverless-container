import os
import eml_parser
from .Processor import Processor


class ProcessorLocal(Processor):
    # EML FILE
    def get_eml_attributes(self, eml_file):
        ep = eml_parser.EmlParser(include_raw_body=True, include_attachment_data=True)
        att_text, attach_name, full_text, attach_names, full_texts, attach_texts = '', '', '', [], [], {}
        parsed_eml = ep.decode_email_bytes(eml_file)
        message_text, header_from = self.get_message_text(parsed_eml)
        attach_names = self.save_attachments_files(parsed_eml)
        for attach_name in attach_names:
            try:
                attachment_path = self.convert_attachment_file(attach_name)
                if os.path.isfile(''.join(attachment_path.split('.')[:-1]) + self.docx_ext):
                    full_text = self.parse_docx(attachment_path)
                else:
                    full_text = self.parse_csv(attachment_path)
                attach_texts[attach_name] = full_text
            except Exception as ex:
                self.worker.error_processor(ex)
                continue
        return attach_texts, message_text, header_from

    def process_eml(self, file):
        result = []
        try:
            with open(file, 'rb') as fhdl:
                eml_file = fhdl.read()
            attach_texts, message_text, header_from = self.get_eml_attributes(eml_file)
            result = self.file_parsing(message_text, attach_texts, header_from)

        except Exception as ex:
            self.worker.error_processor(ex)
            self.log.warning('email processing failed')

        return result

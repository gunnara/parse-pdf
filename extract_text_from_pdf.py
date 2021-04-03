import os
import ocrmypdf


if __name__ == "__main__":
    input_file_name = "tests/fifty_pages_error_list_cropped.pdf"
    ocr_file_name = "tests/fifty_pages_ocr_error_list_cropped.pdf"
    txt_file_name = "tests/fifty_pages_ocr_error_list_cropped.txt"


    os.system(f'ocrmypdf  '
              f'--deskew '
              f'--force-ocr '
              f'--oversample 600 '
              f'--sidecar {txt_file_name}'
              f' {input_file_name}'
              f' {ocr_file_name}')

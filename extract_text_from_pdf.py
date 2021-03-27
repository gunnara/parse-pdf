import os
import ocrmypdf


if __name__ == '__main__':
    input_file_name = 'tests/fifty_pages_error_list_cropped.pdf'
    ocr_file_name = 'tests/fifty_pages_ocr_error_list_cropped.pdf'
    txt_file_name = 'tests/fifty_pages_ocr_error_list_cropped.txt'
    os.system(f'ocrmypdf  --deskew --force-ocr --oversample 1200 --sidecar {txt_file_name} {input_file_name}'
              f' {ocr_file_name}')




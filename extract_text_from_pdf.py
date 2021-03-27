import os
import ocrmypdf


if __name__ == '__main__':
    input_file_name = 'results/error_list_cropped.pdf'
    ocr_file_name = 'results/ocr_error_list_cropped.pdf'
    txt_file_name = 'results/ocr_error_list_cropped.txt'
    os.system(f'ocrmypdf --force-ocr --sidecar {txt_file_name} {input_file_name} {ocr_file_name}')




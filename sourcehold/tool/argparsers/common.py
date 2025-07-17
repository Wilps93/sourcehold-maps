import argparse

file_input_file_output = argparse.ArgumentParser(add_help=False)
file_input_file_output.add_argument("--input", help="input file (.aiv)", required=True)
file_input_file_output.add_argument("--output", help="output file (.aivjson)", required=False)

multiple_file_input_folder_output = argparse.ArgumentParser(add_help=False)
multiple_file_input_folder_output.add_argument("--input", help="input files", nargs='+', required=True)
multiple_file_input_folder_output.add_argument("--output", help="output folder")

main_parser = argparse.ArgumentParser(
    prog="aiv2json_converter.exe",
    description="Конвертер Stronghold .aiv в .aivjson (JSON).\n\nПример использования:\n  aiv2json_converter.exe convert aiv --input caliph1.aiv --output caliph1.aivjson\n\nДля пакетной конвертации используйте цикл в cmd:\n  for %f in (*.aiv) do aiv2json_converter.exe convert aiv --input \"%f\" --output \"%~nf.aivjson\"\n",
    formatter_class=argparse.RawTextHelpFormatter
)
main_parser.add_argument("--debug", action="store_true", default=False, help="debug mode")

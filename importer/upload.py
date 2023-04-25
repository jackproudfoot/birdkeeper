from metadata.extract import extract_metadata
from metadata.util import sample_frames
import argparse
from pathlib import Path
from importer.import_media import import_media, import_plan

def main(args):
    media_file = Path.cwd().joinpath(args.filename).resolve()
    harddrive_path = Path.cwd().joinpath(args.harddrive).resolve()
    
    plan = import_plan(media_file, harddrive_path, debug=False)
    import_media(plan, debug=False)

    #extract_metadata(media_file, debug=True)

    #metadata_file = video_file.with_suffix(video_file.suffix + '.json')

    #metadata = flightpath_parser.sample_frames(metadata_file)

    #print(metadata)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Rainforest Xprize Uploader')

    arg_parser.add_argument('filename')
    arg_parser.add_argument('harddrive')

    args = arg_parser.parse_args()

    main(args)

   
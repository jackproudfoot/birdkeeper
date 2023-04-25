from math import floor, trunc

'''
Sample the frame data in the metadata file at specified rate
'''
def sample_frames(frames, sample_rate = 0.01):
    # Determine sampling jump, with minimum of 15 samples
    max_jump = trunc(len(frames) / 15)
    sampling_jump = min(trunc(sample_rate * 10000), max_jump)

    # Sample frame data
    samples = frames[::sampling_jump]

    return samples

'''
Get standard metadata file from media file path
'''
def get_metadata_file(media_file):
    metadata_file = media_file.parent.joinpath('metadata').joinpath(media_file.name).with_suffix(media_file.suffix + '.json')
    return metadata_file
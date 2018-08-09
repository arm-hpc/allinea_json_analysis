import json
import argparse
import map_json_common as mjc
import sys

def generate_out_filename(infileName, startInd, endInd):
    dotInd= infileName.rfind(".")
    slashInd= infileName.rfind("/")
    suffix= "_trunc" + str(startInd) + "-" + str(endInd)
    outFName= infileName + suffix if dotInd < 0 or (slashInd > 0 and dotInd < slashInd) else \
            infileName[:dotInd] + suffix + infileName[dotInd:]
    return outFName
#### End of function generate_out_filename

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Takes a start and end index" +
    " and truncates the samples in a JSON file to contain only the given" +
    " samples.") 

    # Add a file to read input from
    parser.add_argument("infile", help="JSON format file which has been " +
            "exported from an Arm MAP file")
    # Add a file to read metrics from
    parser.add_argument("startInd", help="Zero based index of the sample number" +
            " from which to start (inclusive)", type=int, default=0)
    parser.add_argument("endInd", help="Zero based index of the sample number" +
            " at which to end (inclusive)", type=int, default=-1)

    # Parse the arguments
    args = parser.parse_args()
    
    # Open the JSON file for reading
    with open(args.infile, "r") as f:
        profileDict = json.load(f)

    # Ensure that the number of samples we want to obtain are in the right range
    if (args.startInd < 0 or args.startInd >= args.endInd or 
        args.endInd >= mjc.get_sample_count(profileDict)):
        print("Invalid index range [" + str(args.startInd) + ", " + str(args.endInd) + "]")
        sys.exit(1)

    mjc.truncate_profile(profileDict, args.startInd, args.endInd)

    outFileName= generate_out_filename(args.infile, args.startInd, args.endInd)
    with open(outFileName, "w") as f:
        json.dump(profileDict, f, sort_keys=True, indent=4)
    print("Truncated JSON samples written to " + outFileName)
#### End of main function

# AWS Kinesis Video Stream (KVS) retention modifier
While manually updating ~5k KVS streams sounds exiting, I'm certainly not going to do it and don't want anyone else to have to do it either.

This repo will allow users to update as many KVS as they want so long as the ARNs are included in the required file; it'll figure out the rest.

For our purposes, the retention period is being set to 24 hours.

## Things to keep in mind
- Set your AWS profile info @ top (using `default` profile and `us-east-1` region as default)
- Don't forget the proxy!
- Each ARN will trigger two API calls -- you may need to break up the list in order to not breach limits!
- You'll need to leverage the path/file in the `main` function as this path is used elsewhere (or mod all to your own)
- Runs generate files (`audit.txt` or `error.txt`) that are **not** timestamped -- if you re-run the job it'll append data to existing files
- The original ARN file does not get modified on success; if you re-run the job it will re-assess any mitigated KVS which will waste time and API calls
- I haven't tested the failure mode b/c I haven't been able to trigger it; YMMV
- Yes, this can be run asyncronously which will make it run *much* faster however, I also want this to run with each being a blocker for the next and since we're exiting on failure anyways...
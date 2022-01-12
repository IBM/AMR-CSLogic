# amr-verbnet-semantics

## Install
Please read [INSTALLATION.md](./INSTALLATION.md)

## Note
- how to clear a cache
  - This implementation uses a cache to speed up the AMR parser. A snapshot is stored on disk to store the cache permanently. The file name of the snapshot takes this format `snapshot.pickle_%Y-%m-%d_%H-%M-%S`. Here is an example of a file name; `snapshot.pickle_2021-10-06_14-52-41`
  - If you want to delete snapshot files, use `bash scripts/remove_snapshot.sh /`. Then please start up the server again to clear a cache. The method is written in [INSTALLATION.md](./INSTALLATION.md). 

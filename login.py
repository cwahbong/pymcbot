from mc import net, util

import argparse
import sys

def main(args):
  util.logConfig(args.filelog, sys.stderr)

  connector, encrypted = net.login(args.host, args.port, args.username)
  print("Encrypted: {}".format(encrypted))
  with connector:
    pass

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--host", type=str, default="127.0.0.1")
  parser.add_argument("--port", type=int, default=25565)
  parser.add_argument("--username", type=str, default="login_tester")
  parser.add_argument("--filelog", nargs='?', const="login.log")
  main(parser.parse_args())

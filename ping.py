from mc import net, util

import argparse
import sys

def main(args):
  util.logConfig(args.filelog, sys.stderr)

  response = net.ping(args.host, args.port)
  if response is not None:
    description = response["description"]
    players_online = response["players"]["online"]
    players_max = response["players"]["max"]
    print("Server:", description)
    print("Players: {}/{}".format(players_online, players_max))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--host", type=str, default="127.0.0.1")
  parser.add_argument("--port", type=int, default=25565)
  parser.add_argument("--filelog", nargs='?', const="ping.log")
  main(parser.parse_args())

from mc import net

import argparse

def main(args):
  response = net.ping(args.host, args.port)
  description = response["description"]
  players_online = response["players"]["online"]
  players_max = response["players"]["max"]
  print("Server:", description)
  print("Players: {}/{}".format(players_online, players_max))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--host", type=str, default='127.0.0.1')
  parser.add_argument("--port", type=int, default=25565)
  main(parser.parse_args())

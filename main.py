import re
import csv
import sys

import click

def matches_switch_open(line):
  return line == 'switch -regexp [string tolower [HTTP::path]] {'

def matches_switch_close(line):
  return line == 'default {'

def matches_pattern(line):
  pattern = re.compile(r"\"(.+)\" {")
  return re.search(pattern, line)

def matches_rule(line):
  pattern = re.compile(r"(.+) \"?(.+)\"?")
  return re.search(pattern, line)

@click.command()
@click.option('--irules', type=click.File('r'))
def parse(irules):
  is_inside_switch = False
  current_rule = {}

  fieldnames = ['pattern', 'command', 'argument']
  writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
  writer.writeheader()

  for line in map(str.strip, irules):
    if not is_inside_switch and matches_switch_open(line):
      is_inside_switch = True
    elif is_inside_switch and matches_switch_close(line):
      break
    elif is_inside_switch:
      pattern_match = matches_pattern(line)
      rule_match = matches_rule(line)

      if line[0] == '#':
        continue
      elif current_rule == {} and pattern_match:
        current_rule['pattern'] = pattern_match[1]
      elif current_rule['pattern'] and line == '}':
        writer.writerow(current_rule)
        current_rule = {}
      elif current_rule['pattern'] and rule_match:
        current_rule['command'] = rule_match[1]
        current_rule['argument'] = rule_match[2]

if __name__ == '__main__':
  parse()

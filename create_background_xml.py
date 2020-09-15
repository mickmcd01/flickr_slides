import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--slides", help="full path to the slides directory")
args = parser.parse_args()

file_list = []
for pic in os.listdir(args.slides):
    if pic.endswith(".jpg"):
        file_list.append(pic)

with open('/home/mick/wallpaper.xml', 'w') as xml:
    xml.write('<background>\n\t<static>\n\t\t<duration>60.00</duration>\n')
    full_path = os.path.join(args.slides, file_list[0])
    xml.write('\t\t<file>%s</file>\n\t</static>\n' % full_path)
    from_path = full_path

    for idx, entry in enumerate(file_list):
        if idx == 0:
            continue

        xml.write('\t<transition>\n\t\t<duration>2.00</duration>\n')
        xml.write('\t\t<from>%s</from>\n' % from_path)
        to_path = os.path.join(args.slides, entry)
        xml.write('\t\t<to>%s</to>\n' % to_path)
        xml.write('\t</transition>\n')
        from_path = to_path

        xml.write('\t<static>\n\t\t<duration>60.00</duration>\n')
        xml.write('\t\t<file>%s</file>\n' % to_path)
        xml.write('\t</static>\n')

    xml.write('</background>\n')

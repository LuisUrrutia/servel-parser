#!/usr/bin/jython
# -*- coding: utf-8 -*-

import os
import sys
import csv
import string
import argparse

sys.path.append("pdfbox-app-2.0.7.jar")

import org.apache.pdfbox.pdmodel.PDDocument as PDDocument
import org.apache.pdfbox.text.PDFTextStripperByArea as PDFTextStripperByArea
import java.awt.geom.Rectangle2D.Float as r2df

MAX_ROWS_PER_PAGE = 65
START_Y = 66.204
TEXT_HEIGHT = 4.6690006
EVEN_OFFSET = 3.3230094
ODD_OFFSET = 3.3229994


def get_pdf_document(name):
    with open(name, "rb") as f:
        pdf = f.read()
        return PDDocument.load(pdf)


def get_province_and_area(document):
    stripper = PDFTextStripperByArea()
    stripper.addRegion("area", r2df(483.397, 28.007, 255.456, 4.760))
    stripper.addRegion("province", r2df(190.717, 40.247, 28.445, 4.760))

    page = document.getPage(0)
    stripper.extractRegions(page)

    province_and_area = {}
    for region in stripper.getRegions():
        province_and_area[region] = stripper.getTextForRegion(region).strip()

    return province_and_area if province_and_area else None


def get_row(page, offset):
    stripper = PDFTextStripperByArea()

    stripper.addRegion("name", r2df(23.965, START_Y + offset, 261.576, TEXT_HEIGHT))
    stripper.addRegion("nin", r2df(285.541, START_Y + offset, 55.512, TEXT_HEIGHT))
    stripper.addRegion("sex", r2df(341.053, START_Y + offset, 16.006, TEXT_HEIGHT))
    stripper.addRegion("address", r2df(380.581, START_Y + offset, 210.96, TEXT_HEIGHT))
    stripper.addRegion("circumscription", r2df(591.541, START_Y + offset, 200.232, TEXT_HEIGHT))
    stripper.addRegion("place", r2df(791.773, START_Y + offset, 17.334, TEXT_HEIGHT))

    stripper.extractRegions(page)

    row = {}
    for region in stripper.getRegions():
        value = stripper.getTextForRegion(region).strip()
        if value:
            row[region] = value

    return row if row else None


def get_records_from_page(document, num):
    page = document.getPage(num)
    accumulated_offset = 0

    records = []
    for r in range(0, MAX_ROWS_PER_PAGE):
        row = get_row(page, accumulated_offset)

        offset = EVEN_OFFSET if r % 2 == 0 else ODD_OFFSET
        accumulated_offset += offset + TEXT_HEIGHT

        if row:
            records.append(row)

    return records


def get_filename_from_path(path):
    path = path.lower().split(os.sep)[-1]
    path = path.split(".")
    if len(path) > 1:
        path = path[:-1]
    return "".join(path)


def safe_filename(filename):
    equivalents = {
        "á": "a",
        "é": "e",
        "í": "í",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "ni",
        "'": ""
    }
    whitelist = "-_.() %s%s" % (string.ascii_letters, string.digits)

    filename = filename.lower()
    for char in equivalents:
        if char in filename:
            filename = filename.replace(char, equivalents[char])

    return ''.join(c for c in filename if c in whitelist)


def normalize_row(row):
    fields = ["name", "nin", "sex", "address", "circumscription", "place"]

    for key in fields:
        if key not in row:
            row[key] = ''
    return row


def results_to_cli(results):
    for row in results:
        row = normalize_row(row)

        print '%-60s %12s %3s %-80s %30s %5s' % (row["name"], row["nin"], row["sex"], row["address"],
                                                 row["circumscription"], row["place"])


def results_to_csv(filename, records):
    with open("{}.csv".format(filename), 'ab') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for row in records:
            row = normalize_row(row)
            writer.writerow([row["name"].encode("utf-8"), row["nin"], row["sex"], row["address"].encode("utf-8"),
                             row["circumscription"].encode("utf-8"), row["place"]])


def main(args):
    document = get_pdf_document(args.file)
    max_pages = document.getNumberOfPages()

    if args.count:
        print("This PDF has {0} pages".format(max_pages))
        return

    start_page = args.start - 1 if args.start and args.start >= 0 else 0
    end_page = args.end if args.end and args.end <= max_pages else max_pages

    province_and_area = get_province_and_area(document)

    filename = province_and_area["province"] if "province" in province_and_area else None
    if filename is None:
        filename = get_filename_from_path(args.file)

    filename = safe_filename(filename)

    for i in range(start_page, end_page):
        records = get_records_from_page(document, i)

        if args.output == "cli":
            results_to_cli(records)
        elif args.output == "csv":
            results_to_csv(filename, records)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str,
                        help="path to pdf file")
    parser.add_argument("--start", type=int,
                        help="Start from page")
    parser.add_argument("--end", type=int,
                        help="Until to page")
    parser.add_argument("--count", action='store_true',
                        help="Get numbers of pages")
    parser.add_argument("--output", type=str, choices=["csv", "cli"], default="cli",
                        help="Get numbers of pages")
    args = parser.parse_args()

    main(args)


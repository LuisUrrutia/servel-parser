# Servel Parser

Jython script to extract the information of Chilean citizens qualified to vote according to PDFs provided by Servel

![Servel PDF](https://raw.githubusercontent.com/LuisUrrutia/servel-parser/master/screenshot/screenshot.png "Extracting info from PDF")

## Getting Started

This project is intended to show how we can easily extract sensitive information from potential chilean voters through PDFs provided by Servel (Chilean Electoral Service).

### Prerequisites

You need two things to use this script:

```
Jython 2.7.1
Apache PDFBox
```

### Usage

If you have Jython installed and the Servel PDFs downloaded, you can run:

```
$ jython extract.py --output csv A1501001.pdf
```

This will create a CSV file with the extracted data

For more info, you can run:

```
$ jython extract.py -h
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
Apache PDFBox file is licensed under Apache License v2.0.

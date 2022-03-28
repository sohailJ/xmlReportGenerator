import xml.etree.cElementTree as ET
import csv


def get_level_and_sequence():
    return


def generate_bs_report_line(root, name, hierarchy_code):
    level = len(hierarchy_code)-1
    sequence = hierarchy_code[-1]
    record = ET.SubElement(root, 'record', id=f'account_financial_report_line_ee_{hierarchy_code}',
                           model='account.financial.html.report.line')
    ET.SubElement(record, 'field', name='name').text = name
    ET.SubElement(record, 'field', name='code').text = f'EE_{hierarchy_code}'
    ET.SubElement(record, 'field', name='level', eval=str(level))
    ET.SubElement(record, 'field', name='sequence', eval=str(sequence))

    if level == 0:
        ET.SubElement(record, 'field', name='financial_report_id', ref='account_financial_report_l10n_ee_balance_sheet')
        ET.SubElement(record, 'field', name='domain', eval='')

    if level >= 1:
        ET.SubElement(record, 'field', name='parent_id', ref=f'account_financial_report_line_ee_{hierarchy_code[:-1]}')

    if level >= 2:
        ET.SubElement(record, 'field', name='groupby').text = 'account_id'
        ET.SubElement(record, 'field', name='domain', eval=f"[('account_id.code', '=ilike', '{hierarchy_code}%')]")
        ET.SubElement(record, 'field', name='formulas').text = 'sum'

    return root


def generate_bs_first_line():
    root = ET.Element('odoo')
    record = ET.SubElement(root, 'record', id='account_financial_report_l10n_ee_balance_sheet',
                           model='account.financial.html.report')
    ET.SubElement(record, 'field', name='name').text = 'Balance Sheet'
    ET.SubElement(record, 'field', name='date_range', eval='False')
    ET.SubElement(record, 'field', name='parent_id', eval='l10n_ee.account_reports_ee_statements_menu')
    return root


if __name__ == '__main__':
    root = generate_bs_first_line()
    path = './src/source.csv'
    with open('./src/source.csv') as csv_file:
        csv_reader = csv.reader(csv_file)
        is_header = True
        for row in csv_reader:
            if row[0] == '' and row[1] != '':
                root = generate_bs_report_line(root, row[1], row[2])
    tree = ET.ElementTree(root)
    tree.write('bs_report.xml')

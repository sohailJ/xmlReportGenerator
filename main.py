import xml.etree.cElementTree as ET
import csv


def get_level_and_sequence():
    return


def compute_hierarchy_code(level_sequence):
    level = 1
    hierarchy_code = ''
    while level_sequence.get(level):
        hierarchy_code += str(level_sequence[level])
        level += 1
    return hierarchy_code


def generate_bs_report_line(root, name, level, hierarchy_code):
    level = len(hierarchy_code) - 1
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

    path = 'src/bs_source.csv'
    accounts = [['id', 'name', 'code', 'user_type_id/id', 'reconcile']]
    account_code_length = 6
    id_prefix = 'ee_coa_'
    hierarchy_account = {}

    # report and account csv generation
    level_sequence = {}
    root = generate_bs_first_line()
    with open(path) as csv_input_file:
        csv_reader = csv.reader(csv_input_file)
        for row in csv_reader:
            if row[0] != '' and row[1] != '':
                level = int(row[1])
                name = row[0]
                if level > 0:
                    if level_sequence.get(level):
                        level_sequence[level] += 1
                        superior_level = level + 1
                        while level_sequence.get(superior_level):
                            del level_sequence[superior_level]
                            superior_level += 1
                    else:
                        level_sequence[level] = 1
                    root = generate_bs_report_line(root, name, level - 1, compute_hierarchy_code(level_sequence))
                else:
                    hierarchy_code = compute_hierarchy_code(level_sequence)
                    if hierarchy_account.get(hierarchy_code):
                        account_code_last = hierarchy_account[hierarchy_code][-1]
                        account_code = account_code_last[len(hierarchy_code):]
                        account_code = hierarchy_code + str(int(account_code[::-1]) + 1)[::-1]
                        hierarchy_account[hierarchy_code].append(account_code)
                    else:
                        account_code = hierarchy_code + '1' * (account_code_length - len(hierarchy_code))
                        hierarchy_account[hierarchy_code] = [account_code]

                    accounts_row = [id_prefix + account_code, name, account_code, '', 'False']
                    accounts.append(accounts_row)
    with open('account.account.template.csv', 'w') as csv_output_file:
        csv_writer = csv.writer(csv_output_file, quotechar='"')
        for account in accounts:
            csv_writer.writerow(account)

    tree = ET.ElementTree(root)
    tree.write('bs_report.xml')

import re
import os
import unittest
import tempfile
import gzip
import shutil

def compare(path1, path2):
    r1 = open(path1)
    r2 = open(path2)
    result = not len(set(r1.readlines())^set(r2.readlines()))
    r1.close()
    r2.close()
    return result

def pvactools_directory():
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

mock_fhs = []
def mock_ncbiwww_qblast(algorithm, reference, peptide, entrez_query, word_size, gapcosts, hitlist_size):
    base_dir      = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    test_data_dir = os.path.join(base_dir, "tests", "test_data", "blast_responses")
    fh = open(os.path.join(test_data_dir, 'response_{}.xml'.format(peptide[0:100])), 'r')
    mock_fhs.append(fh)
    return fh

def mock_netchop_netmhcstabpan(data, files, path, test_file):
    reader = open(os.path.join(
        path,
        test_file
    ), mode='rb')
    response_obj = lambda :None
    response_obj.status_code = 200
    response_obj.content = reader.read()
    reader.close()
    return response_obj

def close_mock_fhs():
    for fh in mock_fhs:
        fh.close()

def make_response(data, files, path, tool=None):
    if not files:
        if tool is not None:
            filename = 'response_{}_{}_{}.{}.tsv'.format(data['allele'], data['length'], data['method'], tool)
        else:
            filename = 'response_{}_{}_{}.tsv'.format(data['allele'], data['length'], data['method'])
        reader = open(os.path.join(
            path,
            filename
        ), mode='r')
        response_obj = lambda :None
        response_obj.status_code = 200
        response_obj.text = reader.read()
        reader.close()
        return response_obj
    else:
        configfile = data['configfile']
        reader = open(os.path.join(
            path,
            'net_chop.html' if 'NetChop-3.1' in configfile else 'Netmhcstab.html'
        ), mode='rb')
        response_obj = lambda :None
        response_obj.status_code = 200
        response_obj.content = reader.read()
        reader.close()
        return response_obj

def generate_class_i_call(method, allele, length, input_file):
    return generate_prediction_calls(method, allele, length, input_file, 'http://tools-cluster-interface.iedb.org/tools_api/mhci/')

def generate_class_ii_call(method, allele, length, input_file):
    return generate_prediction_calls(method, allele, length, input_file, 'http://tools-cluster-interface.iedb.org/tools_api/mhcii/')

def generate_prediction_calls(method, allele, length, input_file, url):
    reader = open(input_file, mode='r')
    text = reader.read()
    reader.close()
    return unittest.mock.call(url, data={
        'sequence_text': ""+text,
        'method':        method,
        'allele':        allele,
        'length':        length,
        'user_tool':     'pVac-seq',
    })

def gunzip_file(zipped_file_path, suffix=None):
    unzipped_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    with gzip.open(zipped_file_path, 'rb') as f_in, open(unzipped_file.name, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return unzipped_file.name

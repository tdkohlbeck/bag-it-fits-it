from subprocess import call
import os, platform, re, shutil
import bagit, xmltodict

errors = {
    'fits': (
        '| ERROR!\n'
        '| unable to find a fits directory!\n'
        '| please specify a location using the --fits option\n'
        '| or place the fits directory in your script folder\n'
    ),
    'spaces': (
        '| ERROR!\n'
        '| please remove all spaces from the output directory name'
        '| note: not sure if this is true for full Windows paths...'
    )
}

def make_dir(filepath):
    if os.path.exists(filepath):
        user_choice = input('| WARNING! ' + filepath + ' exists. Overwrite? [Y/n]: ')
        while True:
            if 'y' in user_choice or '':
                shutil.rmtree(filepath)
                break
            elif 'n' in user_choice:
                print('| WARNING! using in-place ' + filepath)
                return
            else:
                user_choice = input('Sorry? didn\'t quite catch that [Y/n]: ')
    os.makedirs(filepath)

def copy_dir(original_dir, copy_dir):
    if os.path.exists(copy_dir):
        user_choice = input('| WARNING! ' + copy_dir + ' exists. Overwrite? [Y/n]: ')
        while True:
            if 'y' in user_choice or '':
                shutil.rmtree(copy_dir)
                break
            elif 'n' in user_choice:
                print('| WARNING! using in-place ' + copy_dir)
                return
            else:
                user_choice = input('Sorry? didn\'t quite catch that [Y/n]: ')
    shutil.copytree(original_dir, copy_dir)

def run_fits(in_dir, out_dir, fits_dir=None):
    is_win = platform.system() == 'Windows' # special child
    fits_script = r'\fits.bat' if is_win else '/fits.sh'
    if not fits_dir:
        print('| WARNING! no fits location given, searching script directory...')
        for item in os.listdir('.'):
            is_fits = re.search(r'(fits)', item)
            is_dir = os.path.isdir(item)
            if is_fits and is_dir:
                print('| SUCCESS! fits directory found!')
                fits_dir = item
        if not fits_dir:
            print(errors['fits'])
            quit()
    make_dir(out_dir)
    print('| FITS! running on working directory:')
    call([
        fits_dir + fits_script, '-r',
        '-i', in_dir + 'data/',
        '-o', out_dir,
        '-x'
    ])
    print('| SUCCESS! working directory successfully FITSed! :)')


def create_bags(in_dir, master_dir, working_dir):
    copy_dir(in_dir, master_dir)
    bag = bagit.make_bag(master_dir)
    bag.save()
    copy_dir(master_dir, working_dir)


def validate_bag(bag_dir):
    bag = bagit.Bag(bag_dir)
    good = 'VALIDATED! bag at ' + bag_dir
    bad = 'CORRUPTED! bag at ' + bag_dir
    result = good if bag.is_valid() else bad
    print('| ' + result)


def camel_case_to_spaces(string):
    converted = re.sub(r'(.)([A-Z][a-z]+)', r'\1 \2', string)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', converted).title()


# overload path primary with backup, appending sub
def overload_path(primary_dir, backup_dir, sub_dir=''):
    if primary_dir:
        return primary_dir + sub_dir
    else:
        return backup_dir + sub_dir

# structured dict to serial (flat) dict
def flattenDict(obj, delim):
    val = {}
    for i in obj:
        if isinstance(obj[i], dict):
            get = flattenDict(obj[i], delim)
            for j in get:
                val[ i + delim + j ] = get[j]
        else:
            val[i] = obj[i]
    return val


def xml_to_flat_dict(xml_filepath):
    with open(xml_filepath) as report:
        dict_report = xmltodict.parse(report.read())
        return flattenDict(dict_report, '__')

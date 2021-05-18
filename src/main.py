import pushshift

if __name__ == '__main__':
    files = pushshift.get_files_to_dl('2009-04')
    print(list(files))

'''
Input: 2 image tag artifacts 
Retrieves filenames that were not analyzed
Output: `results.csv` file with "image tag, filename,"
'''
import os
import sys
import shutil
import docker
import subprocess

_COVERAGE_SCRIPT = 'infer-coverage.py'
_FIND_PATH_SCRIPT = 'find-src.py'
_DOCKER_REPO = 'bugswarm/images'
_TRAVIS_DIR = '/home/travis/build/failed'
_ARTIFACTS = ['SynBioDex-libSBOLj-88818413',
              'winder-Universal-G-Code-Sender-172454077']
_DOCKER_CLIENT = docker.from_env()


def _get_docker_image_tag(image_tag):
    '''
    args: image tag name
    returns: image tag: /bugswarm/images:image_tag_name
    '''
    return '{}:{}'.format(_DOCKER_REPO, image_tag)


def _run_container(image_tag):
    '''
    given an image tag, run a container

    args: image tag name
    return: container name    
    '''
    docker_image_tag = _get_docker_image_tag(image_tag)
    container = _DOCKER_CLIENT.containers.run(image=docker_image_tag, \
                command='/bin/bash',tty=True,name='c1', \
                detach=True)
    print("Running container {}".format(container.name))
    return container.name


def _run_command(command):
    '''
    run commands

    args: command
    return: process, stdout, stderr, success/error
    '''
    process = subprocess.Popen(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    ok = process.returncode == 0
    return process, stdout, stderr, ok


def _build_infer_image():
    '''
    builds infer image
    '''
    build_cmd = 'docker build -t infer .'
    print('Building infer image')

    try:
        process = subprocess.Popen(build_cmd, shell=True)
    except:
        print('Failed to build infer image')
        sys.exit(1)


def _check_infer_image():
    '''
    check if infer image exists
    if it doesn't exist, build infer image
    '''
    command = 'docker inspect image infer'
    _, stdout, stderr, ok = _run_command(command)
    
    if stdout == '[]':
        _build_infer_image()

    # wait until infer image is built
    while stdout == '[]':
        _, stdout, stderr, ok = _run_command(command) 


def _copy_path_to_local(infer_ctr):
    '''
    copy `path.txt` to local current working directory
    args: infer container name
    '''
    copied = False
    container_path = '/root/home/path.txt'
    local_path = os.getcwd() + '/path.txt'

    while not copied:
        command = 'docker cp {}:{} {}'.format(infer_ctr, container_path, 
                                              local_path)
        try:
           _, stdout, stderr, ok = _run_command(command)
           print("Copying path.txt from infer container to local dir")
           if ok:
               copied = True
        except:
           sys.exit(1)

    print('Copied path.txt to local working directory')


def _find_src_path(infer_ctr):
    '''
    find path of source file in artifact container
    will write the path of source file in a file `path.txt`
    
    args: infer container name
    '''
    command = 'docker exec {} python3 /root/home/find-src.py'.format(infer_ctr)
    print(command)
 
    process = subprocess.Popen(command, shell=True)
    ok = process.returncode == 0
    print("Finding path name of source files in this container")
 
    if ok == 0:
        print("Succeeded in finding path name of source files in container")
        _copy_path_to_local(infer_ctr)
    else:
        print("Failed to find path name of source files in container")
        sys.exit(1)


def _read_path(filename):
    '''
    reads line from file
    args: file
    returns: line
    '''
    f = open(filename, "r")
    return f.readline()


def _move_coverage_script(infer_ctr):
    ''' 
    move coverage script from host directory
    into src directory of failed build in infer container.
    
    args: infer container name
    returns: path of the source directory in failed build
    '''
    src_path = _read_path('path.txt')
    local_dir = os.getcwd() + '/infer-coverage.py'

    try:
        _run_command('docker cp {} {}:{}/{}'.format(local_dir, infer_ctr,
                                                src_path, _COVERAGE_SCRIPT))
    except:
        print("Failed to move coverage script to source directory")
        sys.exit(1)
   
    print("Successfully moved coverage script to source directory")
    return src_path    


def _setup_in_container(infer_ctr):
    '''
    performs updates, installs maven and python3 in infer container
    args: infer container name
    '''
    # apt update
    command = 'docker exec {} apt update'.format(infer_ctr)
    try:
        _, stdout, stderr, ok = _run_command(command)
    except:
        print("Failed `apt update` in infer container: {}".format(stderr))
        sys.exit(1)
    if ok:
        print('apt update')
 
    # installing maven
    command = 'docker exec {} apt --yes install maven'.format(infer_ctr)
    try:
        _, stdout, stderr, ok = _run_command(command)
    except:
        print("Failed `apt install maven`: {}".format(stderr))
        sys.exit(1)
    if ok:
        print('apt install maven')

    # installing python3
    command = 'docker exec {} apt --yes install python3'.format(infer_ctr)
    try:
        _, stdout, stderr, ok = _run_command(command)
    except:
        print("Failed `apt install python3`: {}".format(stderr))
        sys.exit(1)
    if ok:
        print('apt install python3')


def _run_infer_container():
    '''
    run infer container from infer image
    '''
    container = _DOCKER_CLIENT.containers.run(image='infer', \
                command='/bin/bash',tty=True,name='infer-1', \
                detach=True)
    print("Running infer container: {}".format(container.name)) 
    return container.name


def _copy_to_local(container_name):
    '''
    copies failed build from container to local directory
    args: name of container to copy from
    '''
    # create a /temp directory in host
    local_path = os.getcwd() + '/temp'
    
    try:
        os.mkdir(local_path)
    except FileExistsError:
        print('Directory already exists')
        sys.exit(1)
    
    print('About to copy to local')
    _run_command('docker cp {}:{} {}'.format(container_name, 
                                             _TRAVIS_DIR, 
                                             local_path))


def _copy_to_container(new_container):    
    ''' 
    copy failed build and local scripts to container 
    args: name of container
    '''
    local_path = os.getcwd() + '/temp'
    new_dir = '/root/home'
    print('About to copy to new container')

    _run_command('docker cp {} {}:{}'.format(local_path, 
                                             new_container, new_dir))
    _run_command('docker cp {} {}:{}'.format(_COVERAGE_SCRIPT, 
                                             new_container, new_dir))
    _run_command('docker cp {} {}:{}'.format(_FIND_PATH_SCRIPT, 
                                             new_container, new_dir))


def _run_infer(src_path, infer_ctr):
    '''
    run infer on source code in infer container
    args: path of source code, name of infer container
    '''
    infer_cmd = 'infer run --debug -- mvn test-compile compile'
    command = 'docker exec -it {} /bin/sh -c "cd {} ; {}" /bin/bash'.format(
               infer_ctr, src_path, infer_cmd) 

    # go to src directory
    try:
        _, stdout, stderr, ok = _run_command(command)
    except:
        print('Failed to run infer: {}'.format(stderr))
        sys.exit(1)

    if ok:
        print('Succeeded in running infer')


def _run_coverage_script(src_path, infer_ctr):
    '''
    run coverage script in infer container
    args: path of source code in infer contaienr
    '''
    run_cov_cmd = 'python3 infer-coverage.py'
    command = 'docker exec -it {} /bin/sh -c "cd {} ; {}" /bin/bash'.format(
              infer_ctr, src_path, run_cov_cmd)
    try:
        _, stdout, stderr, ok = _run_command(command)
    except:
        print(stderr)
        print('Failed to run coverage script: {}'.format(stderr))
    
    if ok:
        print('Succeeded in running coverage script')



def _copy_results_to_local(src_path, infer_ctr):
    ''' 
    copy results.txt into local directory 
    args: path of source directory in infer container
    '''
    src_path += '/results.txt'
    local_path = os.getcwd() + '/results.txt'
    command = 'docker cp {}:{} {}'.format(infer_ctr, 
                                               src_path, local_path)
    
    try:
        _, stdout, stderr, ok = _run_command(command)
        print(stderr)
    except:
        print("Failed to copy path.txt to local dir")
        sys.exit(1)

    print('Succeeded in copying results.txt to local dir')


def _append_to_results_file(image_tag, results_csv):
    ''' 
    appends filenames from results_txt to results_csv 
    args: image tag and results.csv file
    '''
    with open('results.txt') as txt_file:
        for line in txt_file:
            results_csv.write(image_tag+',')
            results_csv.write(line)


def _remove_containers(src_ctr, infer_ctr):
    '''
    removes artifact and infer containers
    args: name of artifact and infer containers
    '''
    # remove artifact container
    command = 'docker rm -f {}'.format(src_ctr)
    _, stdout, stderr, ok = _run_command(command)
    if ok:
        print('Removed artifact container')
    else:
        print('Failed to remove artifact container')
        sys.exit(1)

    # remove infer container
    command = 'docker rm -f {}'.format(infer_ctr)
    _, stdout, stderr, ok = _run_command(command)
    if ok:
        print('Removed infer container')
    else:
        print('Failed to remove infer container')
        sys.exit(1)


def _remove_files(files):
    '''
    remove `path.txt` and `results.txt`
    args: list of files to remove
    '''
    for filename in files:
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print('{} does not exist'.format(filename))
    
    print('Removed path.txt and results.txt')


def _remove_local_temp_dir():
    '''
    remove local directory /temp
    '''
    local_dir = os.getcwd() + '/temp'

    try:
        shutil.rmtree(local_dir)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
        sys.exit(1) 
    
    print('Removed local /temp directory')


def _cleanup(src_ctr, infer_ctr):
    '''
    remove infer and artifact containers
    remove temp files

    args: artifact container name, infer container name
    '''
    _remove_containers(src_ctr, infer_ctr)
    
    files_to_remove = ['path.txt', 'results.txt']
    _remove_files(files_to_remove)
  
    _remove_local_temp_dir()


def main(argv=None):
    '''
    1) install infer if needed
    2) run each artifact as a docker container
    3) run infer on each artifact
    4) run coverage script on source code
    5) outputs results to csv file
    '''

    results_csv = open('results.csv', 'w')
    results_csv.write('image tag,filename,\n')

    _check_infer_image()

    for image_tag in _ARTIFACTS:
        src_ctr = _run_container(image_tag) 
        infer_ctr = _run_infer_container() 

        _setup_in_container(infer_ctr)
        _copy_to_local(src_ctr)
        _copy_to_container(infer_ctr)        
        _find_src_path(infer_ctr)        
        src_path = _move_coverage_script(infer_ctr)
        _run_infer(src_path, infer_ctr)
        _run_coverage_script(src_path, infer_ctr)
        _copy_results_to_local(src_path, infer_ctr)
        _append_to_results_file(image_tag, results_csv)
       
        _cleanup(src_ctr, infer_ctr)
        print('\n------------\n')        
        
if __name__ == '__main__':
    sys.exit(main())

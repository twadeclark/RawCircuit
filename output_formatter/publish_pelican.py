import os


def publish_pelican(config):
    # execute this shell command: C:\Users\twade\git\pelican\pelican C:\Users\twade\projects\PelicanRawCircuit\content -s C:\Users\twade\projects\PelicanRawCircuit\pelicanconf.py -o C:\Users\twade\projects\PelicanRawCircuit\output
    local_content_path = config.get('local_content_path')
    local_pelicanconf = config.get('local_pelicanconf')
    local_publish_path = config.get('local_publish_path')
    os_result = os.system("pelican " + local_content_path + " -s " + local_pelicanconf + " -o " + local_publish_path)
    if os_result != 0:
        print("     Pelican failed to execute. Exiting...")
        return
    print("     Pelican executed.")

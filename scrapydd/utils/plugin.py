import pkg_resources
import json
import sys
from six import next
from .runner import install_requirements


def execute(plugin_name):
    try:
        entry_point = next(pkg_resources.iter_entry_points('scrapydd.plugin', plugin_name))
    except StopIteration:
        sys.stderr.write('Cannot find plugin %s' % plugin_name)
        return sys.exit(1)
    settings = json.loads(input())
    plugin_execute = entry_point.load()
    output = plugin_execute(settings)
    print(output)


def desc(egg_path):
    try:
        distribution = next(pkg_resources.find_distributions(egg_path))
    except StopIteration:
        raise ValueError("Unknown or corrupt egg")

    execute_entry_point = distribution.get_entry_map('scrapydd.plugin.execute')
    desc_entry_point = distribution.get_entry_map('scrapydd.plugin.desc')

    if not execute_entry_point:
        sys.stderr.write('Cannot find plugin execute entrypoint')
        return sys.exit(1)

    if not desc_entry_point:
        sys.stderr.write('Cannot find plugin desc entrypoint')
        return sys.exit(1)

    install_requirements(distribution)
    distribution.activate()

    execute_name = next(iter(execute_entry_point))
    desc_name = next(iter(desc_entry_point))

    plugin_desc = desc_entry_point[desc_name].load()
    output = plugin_desc()
    print(output)


def main():
    cmd = sys.argv[1]
    if cmd == 'execute':
        return execute(sys.argv[2])
    elif cmd == 'desc':
        return desc(sys.argv[2])

if __name__ == '__main__':
    main()
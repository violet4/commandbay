import argparse
import logging

class Namespace(argparse.Namespace):
    log_level: str = 'INFO'


def list_log_levels():
    levels = [
        (a,getattr(logging,a))
        for a in dir(logging)
        if a.upper()==a
        and isinstance(getattr(logging, a), int)
    ]
    return [l[0] for l in sorted(levels, key=lambda a:a[1])]


def parse_args(default_log_level:str=Namespace.log_level) -> type[Namespace]:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--log-level', default=default_log_level, type=str,
        help=f"log level. default: %(default)s; options: {list_log_levels()}",
    )
    args = arg_parser.parse_args(namespace=Namespace)
    return args

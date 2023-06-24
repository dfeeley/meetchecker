import logging
import pathlib
import yaml

from meetchecker.utils import expand_date_macros
from meetchecker.utils import select_from_user

logger = logging.getLogger(__name__)


class DotFile:
    def __init__(self, path=None):
        path = path or "~/.meetchecker.yaml"
        self.path = pathlib.Path(path).expanduser()
        self.data = {}
        if self.exists():
            with open(self.path) as f:
                self.data = yaml.safe_load(f)

    def exists(self):
        return self.path.exists()

    def _get(self, key, as_path=True):
        ret = expand_date_macros(self.data.get(key))
        if ret and as_path:
            ret = pathlib.Path(ret)
        return ret

    @property
    def workdir(self):
        return self._get("workdir")

    @property
    def checks(self):
        return self._get("checks")

    @property
    def last_database(self):
        return self._get("last_database")

    @last_database.setter
    def last_database(self, value):
        self.data["last_database"] = value
        with open(self.path, "w") as f:
            f.write(yaml.dump(self.data))


class Locations:
    def __init__(self, workdir):
        self.workdir = workdir
        self.curdir = pathlib.Path.cwd()
        self.codedir = pathlib.Path(__file__).parent.resolve()
        self.priority_order = [
            path for path in [self.workdir, self.curdir, self.codedir] if path.exists()
        ]

    def find_matching_files(self, pattern):
        matches = []
        for parent in self.priority_order:
            matches.extend(parent.glob(pattern))
        return matches

    def find_relative_path(self, relative):
        for parent in self.priority_order:
            test_path = parent / relative
            if test_path.exists():
                return test_path

    def sort_files_by_date(self, files, reverse=True):
        annotated = [(path, path.stat().st_mtime) for path in files]
        annotated.sort(key=lambda i: i[1], reverse=reverse)
        return [_[0] for _ in annotated]

    def resolve_file_relative_to_first_known_dir(self, relative_path):
        if not self.priority_order:
            raise ValueError(f"No known locations found, this is odd")
        return self.priority_order[0] / relative_path

    @property
    def known_directories_as_str(self):
        ret = "\n * ".join(str(path) for path in self.priority_order)
        return f"\n * {ret}\n"

    def resolve_database(self, param, ask, last_database):
        if param and not ask:
            # user has supplied a database param on the cmd line -- this takes priority
            path = pathlib.Path(param)
            if path.is_absolute():
                if path.exists():
                    return path
                logger.error(
                    f"Could not find the database {param!r} that you specified.  Either pick from the list "
                    "below or Ctrl-C and try again"
                )
            else:
                # its a relative path, try it vs our various search dirs
                found = self.find_relative_path(path)
                if found:
                    return found
                logger.error(
                    f"Could not find the database {param!r} that you specified relative to any of our "
                    f"known directories: "
                    f"{self.known_directories_as_str}"
                    "Either pick from the list below or Ctrl-C and try again"
                )
        elif last_database and not ask:
            last_database_path = pathlib.Path(last_database)
            if last_database_path.exists():
                return last_database_path
        # ask user to select a path
        files_to_choose_from = [
            str(p)
            for p in self.sort_files_by_date(self.find_matching_files(pattern="*.mdb"))
        ]
        if not files_to_choose_from:
            return ValueError(
                "Unable to find any database (.mdb) files to choose from in our known directories "
                f"({self.priority_order}).  Perhaps specifiy a database file on the command line?"
            )
        file = select_from_user(
            files_to_choose_from,
            message="Please select a database from the following",
        )
        if file:
            return pathlib.Path(file)
        raise ValueError("No database selected")

    def resolve_output(self, cmdline_param, database):
        if cmdline_param:
            # user has supplied a output param on the cmd line -- this takes priority
            path = pathlib.Path(cmdline_param)
            if path.is_absolute():
                return path
            else:
                return self.resolve_file_relative_to_first_known_dir(path)
        else:
            return database.with_suffix(".html")

    def resolve_checks(self, cmdline_param, dotfile_checks):
        if cmdline_param:
            # user has supplied a checks param on the cmd line -- this takes priority
            path = pathlib.Path(cmdline_param)
            if path.is_absolute():
                if path.exists():
                    return path
                raise ValueError(
                    f"Could not find the checks file {cmdline_param!r} that you specified."
                )
            else:
                # its a relative path, try it vs our various search dirs
                found = self.find_relative_path(path)
                if found:
                    return found
                raise ValueError(
                    f"Could not find the checks file {cmdline_param!r} that you specified relative to any "
                    "of our known directories: "
                    f"{self.known_directories_as_str}"
                )
        return dotfile_checks

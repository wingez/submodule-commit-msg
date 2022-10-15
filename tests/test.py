import os
import sys
from pathlib import Path
from subprocess import run

import shutil
from typing import Union, List, Dict, Optional

commit_hash_length = "SUBMODULE_HOOK_HASH_LENGTH"
max_commits = "SUBMODULE_HOOK_MAX_COMMIT_SHOWN"


def test_main(tmp_path: Path):
    print(tmp_path)

    directory = tmp_path.parent

    main_repo = directory / 'main'
    sub1 = directory / 'sub1'
    sub2 = directory / 'sub2'

    create_repo(main_repo)
    create_repo(sub1)
    create_repo(sub2)

    add_submodule_to_repo(main_repo, sub1, "testmodule")
    add_submodule_to_repo(main_repo, sub2, "testmodule1")


def test_single_submodule_single_commit(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module = add_submodule_to_repo(folders.main_repo, folders.sub1, "testmodule")
    commit(folders.main_repo, "add submodules", test_module)

    empty_commit_in_folder(test_module, "empty commit")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "new commit", test_module, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "new commit",
        "",
        "Submodule changes:",
        "testmodule:",
        "     empty commit",
        "",
        "End of submodule changes:",
    ]


def test_no_submodule_changes(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module = add_submodule_to_repo(folders.main_repo, folders.sub1, "testmodule")
    commit(folders.main_repo, "add submodules", test_module)

    empty_commit_in_folder(test_module, "empty commit")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "new commit", allow_empty=True)

    assert get_last_commit_message(folders.main_repo) == [
        "new commit",
    ]


def test_multiple_submodules(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    test_module2 = add_submodule_to_repo(folders.main_repo, folders.sub2, "second")
    commit(folders.main_repo, "add submodules", test_module1, test_module2)

    empty_commit_in_folder(test_module1, "empty commit")
    empty_commit_in_folder(test_module2, "another empty commit")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "hello world", test_module1, test_module2, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "hello world",
        "",
        "Submodule changes:",
        "first:",
        "     empty commit",
        "",
        "second:",
        "     another empty commit",
        "",
        "End of submodule changes:",
    ]


def test_max_commits_shown(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodules", test_module1)

    for i in range(10):
        empty_commit_in_folder(test_module1, f"empty commit {i}")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "hello world", test_module1, config={max_commits: 2, commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "hello world",
        "",
        "Submodule changes:",
        "first:",
        "     empty commit 9",
        "     empty commit 8",
        "    ... +8 more",
        "",
        "End of submodule changes:",
    ]


def test_commit_hash(tmp_path):
    commit_size = 3
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodules", test_module1)

    empty_commit_in_folder(test_module1, f"empty commit")
    commit_hash = do_git_command(test_module1, 'rev-parse', 'HEAD')[0][:commit_size]

    install_hook(folders.main_repo)
    commit(folders.main_repo, "hello world", test_module1, config={commit_hash_length: commit_size})

    assert get_last_commit_message(folders.main_repo) == [
        "hello world",
        "",
        "Submodule changes:",
        "first:",
        f"    {commit_hash} empty commit",
        "",
        "End of submodule changes:",
    ]


def test_comparison_commit_source(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodules", test_module1)

    empty_commit_in_folder(test_module1, f"commit 1")
    commit(folders.main_repo, "amend me", test_module1)
    empty_commit_in_folder(test_module1, "commit 2")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "amend me", test_module1, amend=True, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "amend me",
        "",
        "Submodule changes:",
        "first:",
        "     commit 2",
        "     commit 1",
        "",
        "End of submodule changes:",
    ]


def test_replace_commit_msg(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodules", test_module1)
    empty_commit_in_folder(test_module1, f"commit 1")

    install_hook(folders.main_repo)
    commit(folders.main_repo, "amend me", test_module1, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "amend me",
        "",
        "Submodule changes:",
        "first:",
        "     commit 1",
        "",
        "End of submodule changes:",
    ]

    empty_commit_in_folder(test_module1, "commit 2")
    commit(folders.main_repo, "ignore", test_module1, amend=True, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "amend me",
        "",
        "Submodule changes:",
        "first:",
        "     commit 2",
        "     commit 1",
        "",
        "End of submodule changes:",
    ]


def test_hook_amend(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module = add_submodule_to_repo(folders.main_repo, folders.sub1, "testmodule")
    commit(folders.main_repo, "add submodules", test_module)

    empty_commit_in_folder(test_module, "empty commit")
    first_commit_hash = do_git_command(test_module, 'rev-parse', 'HEAD')[0][:8]

    stage_files(folders.main_repo, test_module)

    install_hook(folders.main_repo)
    commit(folders.main_repo, "Test commit")

    assert get_last_commit_message(folders.main_repo) == [
        'Test commit',
        '',
        'Submodule changes:',
        'testmodule:',
        f'    {first_commit_hash} empty commit',
        '',
        'End of submodule changes:',
    ]

    empty_commit_in_folder(test_module, 'another commit')
    second_commit_hash = do_git_command(test_module, 'rev-parse', 'HEAD')[0][:8]

    stage_files(folders.main_repo, test_module)
    commit_amend(folders.main_repo)

    assert get_last_commit_message(folders.main_repo) == [
        'Test commit',
        '',
        'Submodule changes:',
        'testmodule:',
        f'    {second_commit_hash} another commit',
        f'    {first_commit_hash} empty commit',
        '',
        'End of submodule changes:',
    ]


def test_do_nothing_in_repo_with_no_submodules(tmp_path):
    folders = DefaultFolders(tmp_path)
    install_hook(folders.main_repo)
    commit(folders.main_repo, "hello world", allow_empty=True)

    assert get_last_commit_message(folders.main_repo) == ["hello world"]

    # Test so we can also handle empty gitmodules file
    git_modules_file = folders.main_repo / ".gitmodules"
    git_modules_file.touch()
    commit(folders.main_repo, "hello world2", allow_empty=True)

    assert get_last_commit_message(folders.main_repo) == ["hello world2"]


def test_new_module_added(tmp_path):
    folders = DefaultFolders(tmp_path)
    install_hook(folders.main_repo)
    empty_commit_in_folder(folders.main_repo, "hej")

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodule", test_module1)

    assert get_last_commit_message(folders.main_repo) == [
        'add submodule',
        '',
        'Submodule changes:',
        'first:',
        '    Added',
        '',
        'End of submodule changes:',
    ]


def test_new_module_removed(tmp_path):
    folders = DefaultFolders(tmp_path)
    install_hook(folders.main_repo)
    empty_commit_in_folder(folders.main_repo, "hej")
    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodule", test_module1)

    do_git_command(folders.main_repo, "rm", test_module1)
    commit(folders.main_repo, "removed submodule")

    assert get_last_commit_message(folders.main_repo) == [
        'removed submodule',
        '',
        'Submodule changes:',
        'first:',
        '    Removed',
        '',
        'End of submodule changes:',
    ]


def test_insert_message_after_trailers(tmp_path):
    folders = DefaultFolders(tmp_path)

    test_module1 = add_submodule_to_repo(folders.main_repo, folders.sub1, "first")
    commit(folders.main_repo, "add submodules", test_module1)

    install_hook(folders.main_repo)
    msg_file = folders.main_repo / "commit_msg"
    original_commit_msg = [
        "some random commit",
        "",
        "this is not a trailer",
        "",
        "this: isonehowever",
        "thisisoneas: well",
    ]
    msg_file.write_text(os.linesep.join(original_commit_msg))

    assert do_git_command(folders.main_repo, "interpret-trailers", "--parse", msg_file) == [
        "this: isonehowever",
        "thisisoneas: well",
    ]

    commit(folders.main_repo, '', allow_empty=True, commit_msg_file=msg_file)
    assert get_last_commit_message(folders.main_repo) == original_commit_msg

    empty_commit_in_folder(test_module1, f"commit 1")
    commit(folders.main_repo, "ignore", test_module1, amend=True, config={commit_hash_length: 0})

    assert get_last_commit_message(folders.main_repo) == [
        "some random commit",
        "",
        "this is not a trailer",
        "",
        "Submodule changes:",
        "first:",
        "     commit 1",
        "",
        "End of submodule changes:",
        "",
        "this: isonehowever",
        "thisisoneas: well",
    ]


class DefaultFolders:
    def __init__(self, tmp_path: Path):
        self.main_repo = tmp_path / 'main'
        self.sub1 = tmp_path / 'sub1'
        self.sub2 = tmp_path / 'sub2'

        create_repo(self.main_repo)
        create_repo(self.sub1)
        create_repo(self.sub2)


def install_hook(repo: Path):
    hooks_dir = repo / '.git' / 'hooks'
    hook_path = Path(__file__).parent.parent / 'prepare-commit-msg'

    shutil.copy(hook_path, hooks_dir)
    do_command('chmod', '+x', hooks_dir / 'prepare-commit-msg', config={})


def do_command(*command: Union[str, Path], config: Dict) -> List[str]:
    result = run(command, capture_output=True, env={i: str(config[i]) for i in config})
    result.check_returncode()
    return result.stdout.decode().strip().splitlines()


def get_last_commit_message(repo: Path) -> List[str]:
    return do_git_command(repo, 'log', '--format=%B', '-n', '1', 'HEAD', config={})


def do_git_command(repo: Path, *options: str, config: Dict = {}) -> List[str]:
    command = ['git', '-C', repo]
    command.extend(options)

    return do_command(*command, config=config)


def stage_files(repo: Path, *to_stage: Path):
    for file in to_stage:
        run(['git', '-C', repo, 'add', file]).check_returncode()


def add_submodule_to_repo(repo: Path, submodule_path: Path, name: str) -> Path:
    run(['git', '-C', repo, 'submodule', 'add', '--branch', 'master', submodule_path, name]).check_returncode()
    return repo / name


def commit_amend(repo: Path):
    args = ['commit', '--no-edit', '--amend']
    do_git_command(repo, *args)


def commit(repo: Path, commit_msg: str, *to_stage: Path, commit_msg_file: Optional[Path] = None, amend: bool = False,
           allow_empty: bool = False, config={}):
    stage_files(repo, *to_stage)

    args = ['commit', ]

    if amend:
        args.extend(['--amend', '--no-edit'])
    elif commit_msg_file is not None:
        args.extend(["--file", commit_msg_file])
    else:
        args.extend(['-m', commit_msg])

    if allow_empty:
        args.append('--allow-empty')

    do_git_command(repo, *args, config=config)


def empty_commit_in_folder(repo: Path, commit_msg: str):
    commit(repo, commit_msg, allow_empty=True)


def create_repo(repo_path: Path):
    repo_path.mkdir()
    run(['git', '-C', repo_path, 'init']).check_returncode()
    run(['git', '-C', repo_path, 'commit', '-m', 'Initial commit', '--allow-empty']).check_returncode()

#!/usr/bin/env python3
"""
Record bounded, repeatable ROS CLI experiments in a separate ROS domain.

Run after building and sourcing the workspace. --expect-broken is an assertion
about the supplied source checkout; it does not modify validation itself.
"""

import argparse
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys


def main():
    """Start owned processes, record real CLI output, and clean up on failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-broken', action='store_true')
    parser.add_argument('--domain', default='174')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(ROS_DOMAIN_ID=args.domain, ROS2CLI_NO_DAEMON='1',
               PYTHONUNBUFFERED='1',
               ROS_LOG_DIR='/tmp/pr04-ros-logs', QT_QPA_PLATFORMTHEME='none',
               QT_STYLE_OVERRIDE='Fusion', QT_QPA_PLATFORM='xcb')
    env.pop('XDG_CURRENT_DESKTOP', None)
    env.pop('DESKTOP_SESSION', None)
    env['PYTHONPATH'] = str(args.source.resolve() / 'src/patrol') + os.pathsep + (
        env.get('PYTHONPATH', ''))
    processes = []

    def stop(process):
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            try:
                process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)

    with args.output.open('w') as transcript:
        transcript.write('# Реальные команды и вывод PR04\n\n')
        transcript.write(f'ROS_DOMAIN_ID={args.domain}; ROS_DISTRO={env.get("ROS_DISTRO")}\n\n')
        transcript.write(f'Источник patrol: `{args.source.resolve()}`.\n\n')
        transcript.write('Окно turtlesim: без XDG_CURRENT_DESKTOP и DESKTOP_SESSION; '
                         'QT_QPA_PLATFORMTHEME=none, QT_STYLE_OVERRIDE=Fusion, '
                         'QT_QPA_PLATFORM=xcb.\n\n')

        def command(parts, timeout=10, expected=None):
            rendered = shlex.join(parts)
            print('$ ' + rendered, flush=True)
            process = subprocess.Popen(parts, env=env, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True,
                                       start_new_session=True)
            try:
                output, _ = process.communicate(timeout=timeout)
                code = process.returncode
            except subprocess.TimeoutExpired:
                stop(process)
                output, _ = process.communicate(timeout=3)
                code = 124
            transcript.write(f'```console\n$ {rendered}\n{output}\n[exit={code}]\n```\n\n')
            transcript.flush()
            print(output, end='', flush=True)
            if expected is not None:
                assert code == expected, (rendered, code, output)
            return output, code

        def start(parts, suffix):
            log_path = args.output.with_name(suffix)
            log = log_path.open('w')
            process = subprocess.Popen(parts, env=env, stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            processes.append((process, log))
            transcript.write(f'Фоновый запуск: `{shlex.join(parts)}`; лог `{log_path.name}`.\n\n')
            transcript.flush()
            return process, log_path

        def measure(expected_hz):
            output, _ = command(['ros2', 'topic', 'hz', '/turtle1/cmd_vel'], timeout=7)
            rates = [float(rate) for rate in re.findall(r'average rate: ([0-9.]+)', output)]
            assert rates, 'No frequency measurements received'
            assert abs(rates[-1] - expected_hz) < expected_hz * 0.2, rates

        try:
            start(['ros2', 'launch', 'turtle_bringup', 'sim.launch.py'],
                  args.output.stem + '-simulator.txt')
            patrol, patrol_log = start([sys.executable, '-m', 'patrol.patrol'],
                                       args.output.stem + '-patrol.txt')
            output, _ = command(['ros2', 'param', 'get', '/patrol', 'publish_hz'], expected=0)
            assert '10.0' in output
            measure(10.0)
            command(['ros2', 'param', 'set', '/patrol', 'publish_hz', '5.0'], expected=0)
            command(['ros2', 'param', 'get', '/patrol', 'publish_hz'], expected=0)
            measure(5.0)

            output, code = command(['ros2', 'param', 'set', '/patrol', 'publish_hz', '0.0'],
                                   timeout=8)
            if args.expect_broken:
                assert patrol.poll() is not None, 'Broken node did not terminate'
                assert 'ZeroDivisionError' in patrol_log.read_text()
                transcript.write('После запроса нуля процесс patrol завершился; '
                                 'ZeroDivisionError подтверждён в логе ноды.\n\n')
            else:
                assert code != 124
                assert 'failed' in output.lower() or 'unsuccessful' in output.lower()
                output, _ = command(['ros2', 'param', 'get', '/patrol', 'publish_hz'], expected=0)
                assert '5.0' in output
                measure(5.0)
                for name, value in [('linear_speed', '0.8'), ('turn_rate', '-0.5')]:
                    command(['ros2', 'param', 'set', '/patrol', name, value], expected=0)
                command(['ros2', 'topic', 'echo', '/turtle1/cmd_vel', '--once'], expected=0)
                command(['ros2', 'topic', 'type', '/turtle1/pose'], expected=0)
                command(['ros2', 'service', 'call', '/clear', 'std_srvs/srv/Empty', '{}'],
                        expected=0)
                output, _ = command(['ros2', 'action', 'list', '-t'], expected=0)
                assert '/turtle1/rotate_absolute' in output
            transcript.write('Все утверждения сценария выполнены.\n')
        finally:
            for process, log in reversed(processes):
                stop(process)
                log.close()


if __name__ == '__main__':
    main()

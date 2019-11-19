from ipykernel.kernelbase import Kernel
from pexpect import popen_spawn


class RunKernel(Kernel):
    implementation = 'IClojure'
    implementation_version = '1.0'
    language = 'Clojure'
    language_info = {
            'name' : 'Clojure Notebook'
            , 'file_extension' : '.clj'
            , 'mimetype': 'text/plain'
    }
    banner = "Clojure Kernel"
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.child = popen_spawn.PopenSpawn('lein repl', timeout=30000, cwd='/Users/acreed/Desktop/go-jek/promo_worker/')
        self.child.expect('\ncom.gopay.promo.worker.core=> ')

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            self.child.sendline(code)
            # waiting for prompt to show up
            self.child.expect('\ncom.gopay.promo.worker.core=> ')
            response_text = bytes(self.child.before)
            if response_text == b'' or response_text[-1] == b'\n'[-1]:
                # means we got an actual prompt
                pass
            else:
                # means we got just a '> ' characters in the middle of a line
                # so we do another search until we find an actual prompt
                response_text += self.child.after
                self.child.expect('\ncom.gopay.promo.worker.core=> ')
                response_text += self.child.before
            print(response_text)

            stream_content = {'name': 'stdout',
                              'text': response_text.decode('utf-8')}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def do_shutdown(self, restart):
        self.child.kill(signal.CTRL_C_EVENT)

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=RunKernel)

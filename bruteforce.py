from Pyro4 import expose
import time

class Solver:
    def __init__(self, workers=None, input_file_name = None, output_file_name = None):
        self.workers = workers or []
        self.output_file_name = output_file_name
        self.input_file_name = input_file_name

    def solve(self):
        print("Job Started")
        print("Workers: %d" % len(self.workers))

        charset = "abcdefghijklmnopqrstuvwxyz"
        charset_size = len(charset)
        correct_password = "merlin"
        password_len = 6
        password_found = False
        result = ""
        elapsed = 0
        total = charset_size ** password_len
        chunk_size = total // len(self.workers)

        jobs = []
        for i in xrange(len(self.workers)):
            start = i * chunk_size
            end = (i + 1) * chunk_size if i < len(self.workers) - 1 else total
            jobs.append((start, end))

        mapped = []
        for i, (start, end) in enumerate(jobs):
            worker = self.workers[i]
            mapped.append(worker.bruteforce(password_len, start, end, charset, correct_password))

        for m in mapped:
            if hasattr(m, 'value'): 
                result_m, elapsed_m = m.value
            else:
                result_m, elapsed_m = m
            if elapsed_m > 0:
                password_found = True
                result = result_m
                elapsed = elapsed_m
                break

        self.write_to_output_file(password_found, result, elapsed)

        print ("Finished")

    def write_to_output_file(self, password_found, result, elapsed):
        with open(self.output_file_name, 'w') as f:
            if password_found:
                f.write("Password found: {}, time = {}\n".format(result, elapsed))
            else:
                f.write("Password wasn't found\n")
            print ("Written to file")

    @expose
    def bruteforce(self, length, start, end, charset, correct_password):
        charset_size = len(charset)
        start_time = time.time()
        for number in xrange(start, end):
            guess = self.number_to_word(number, length, charset, charset_size)
            if guess == correct_password:
                end_time = time.time()
                elapsed = end_time - start_time
                return guess, elapsed
        return None, 0

    @staticmethod
    def number_to_word(number, length, charset, charset_size):
        word = ['a'] * length
        for i in range(length - 1, -1, -1):
            word[i] = charset[number % charset_size]
            number //= charset_size
        return ''.join(word)
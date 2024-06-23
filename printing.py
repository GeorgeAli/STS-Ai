original_stdout = sys.stdout # Save a reference to the original standard output

with open('x not in list .txt', 'a') as f:
    sys.stdout = f # Change the standard output to the file we created.
    print()
    sys.stdout = original_stdout

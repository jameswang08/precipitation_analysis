import os

directory = './Data/BaselineCleaned'

for filename in os.listdir(directory):
    if filename.endswith('.nc'):
        year_str = filename[:4]
        try:
            year = int(year_str)
            if year < 1981 or year > 2019:
                filepath = os.path.join(directory, filename)
                print(f"Deleting {filepath}")
                os.remove(filepath)
        except ValueError:
            pass

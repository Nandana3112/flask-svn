import subprocess

output = subprocess.check_output(
    [r"C:\Program Files\VisualSVN Server\bin\svn.exe", "info", r"C:\svn\testrepo_wc"],
    universal_newlines=True
)
print(output)
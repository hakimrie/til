1. List of all conda environments
```sh
conda env list
```

2. List of all conda environments and its size
```sh
for env in $(conda info --envs | awk 'NR>2 {print $NF}'); do
    size=$(du -sh "$env" 2>/dev/null | cut -f1)
    echo "$env  --->  $size"
done
```

- `conda info --envs`
    This command lists all Conda environments and their paths.
- `awk 'NR>2 {print $NF}'`
    This filters the output of `conda info --envs`:

    - `NR>2` "skip the first two lines" (which are headers).
    - `{print $NF}` prints the last field (the environment path).
- `size=$(du -sh "$env" 2>/dev/null | cut -f1)`
    - `du -sh "$env"` calculates the disk usage of the environment in a human-readable format.
    - `2>/dev/null` do not show any error messages.
    - `cut -f1` extracts just the size (the first field of `du -sh` output).
- `echo "$env ---> $size"` prints the env path and its size, separated by `--->`

Powershell version
```sh
conda info --envs | ForEach-Object {
    if ($_ -match "^(.*?)(\s+\*)?\s+(.+)$") {
        $path = $Matches[3]
        if (Test-Path $path) {
            $size = (Get-ChildItem -Recurse $path | Measure-Object -Property Length -Sum).Sum
            "{0,-50} {1,10:N2} MB" -f $path, ($size / 1MB)
        }
    }
}
```

**Output**
```
/Users/muhammad.hakim/miniconda3  --->  4.5G
/Users/muhammad.hakim/miniconda3/envs/aip  --->  162M
/Users/muhammad.hakim/miniconda3/envs/cloudstart  --->  461M
/Users/muhammad.hakim/miniconda3/envs/presidio  --->  714M
/Users/muhammad.hakim/miniconda3/envs/telegram-bot  --->  145M
...
```
3. Delete conda env

```sh
conda env remove -n <env-name>
```
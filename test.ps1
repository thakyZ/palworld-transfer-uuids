& "$((Get-Command -Name "pyenv").Source)" shell "3.12.2"

Push-Location -Location (Join-Path -Path $PScriptDir -ChildPath "test")

& "$((Get-Command -Name "python").Source)" "$(Join-Path -Path $PWD -ChildPath "test.py")" $Args;

Pop-Location

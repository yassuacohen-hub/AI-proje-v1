 = Get-Content -Raw .\restore_original.py
 = .IndexOf('original_content = ''''') + 21
 = .IndexOf(''''', )
 = .Substring(,  - )
 =  -replace '        except APIError:', '    except APIError:'
Set-Content -Path .\web_dashboard\tabs\admin_extras.py -Value  -Encoding UTF8

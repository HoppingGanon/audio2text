$str = (pip-licenses -l -f json --no-license-path)
$obj = $str | ConvertFrom-Json

$list = New-Object Collections.ArrayList
(convertfrom-csv (get-content -Raw requirements.txt) -Delimiter "=" -Header 'A','B','C').A | %{
    $name = $_
    $ary = $obj | ?{$_.Name -eq $name}
    if ($ary.length -ne 0) {
        $list.Add($ary[0]) | Out-Null
    }
}

$list | ConvertTo-Json | Out-File -Encoding utf8 'licenses.json'

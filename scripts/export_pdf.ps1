# Export a .docx (or .doc) to PDF with Microsoft Word, read-only, to check layout.
# Usage: pwsh -File export_pdf.ps1 -Docx salida.docx -Pdf salida.pdf
param([Parameter(Mandatory)][string]$Docx, [Parameter(Mandatory)][string]$Pdf)
[string]$src = (Resolve-Path $Docx).Path
[string]$out = [System.IO.Path]::GetFullPath($Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $doc = $w.Documents.Open($src, $false, $true)
    $doc.ExportAsFixedFormat($out, 17)
    $doc.Close(0)
    Write-Output "PDF: $out"
} finally {
    $w.Quit()
}

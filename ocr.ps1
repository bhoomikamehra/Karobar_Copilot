param([string]$ImagePath)

try {
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $asTaskGeneric = [System.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }

    [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime] | Out-Null
    [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime] | Out-Null
    [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime] | Out-Null

    $absPath = (Resolve-Path $ImagePath).Path
    $op = [Windows.Storage.StorageFile]::GetFileFromPathAsync($absPath)
    $asTask = $asTaskGeneric.MakeGenericMethod([Windows.Storage.StorageFile])
    $file = $asTask.Invoke($null, @($op)).Result

    $streamOp = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read)
    $asTaskStream = $asTaskGeneric.MakeGenericMethod([Windows.Storage.Streams.IRandomAccessStream])
    $stream = $asTaskStream.Invoke($null, @($streamOp)).Result

    $decoderOp = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
    $asTaskDecoder = $asTaskGeneric.MakeGenericMethod([Windows.Graphics.Imaging.BitmapDecoder])
    $decoder = $asTaskDecoder.Invoke($null, @($decoderOp)).Result

    $bitmapOp = $decoder.GetSoftwareBitmapAsync()
    $asTaskBitmap = $asTaskGeneric.MakeGenericMethod([Windows.Graphics.Imaging.SoftwareBitmap])
    $bitmap = $asTaskBitmap.Invoke($null, @($bitmapOp)).Result

    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if ($null -eq $engine) {
        $lang = [Windows.Globalization.Language]::new('en-US')
        $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
    }

    $ocrOp = $engine.RecognizeAsync($bitmap)
    $asTaskOcr = $asTaskGeneric.MakeGenericMethod([Windows.Media.Ocr.OcrResult])
    $ocrResult = $asTaskOcr.Invoke($null, @($ocrOp)).Result

    $lines = @()
    foreach ($line in $ocrResult.Lines) {
        $lines += $line.Text
    }
    $lines -join "`n"
} catch {
    Write-Error $_.Exception.Message
}

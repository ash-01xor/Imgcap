import pytest
from unittest.mock import patch, MagicMock , call
from pathlib import Path
from click.testing import CliRunner
from imgcap import generate_caption, output_caption, cli

@pytest.fixture
def mock_image():
    with patch('PIL.Image.open') as mock_open:
        mock_img = MagicMock()
        mock_open.return_value = mock_img
        yield mock_img

@pytest.fixture
def mock_caption_model():
    return MagicMock(return_value=[{"generated_text": "A test caption"}])

def test_generate_caption(mock_image, mock_caption_model):
    result = generate_caption(mock_caption_model, "test_image.jpg", 50)
    assert result == ("test_image.jpg", "A test caption")

def test_generate_caption_error():
    with patch('PIL.Image.open', side_effect=Exception("Test error")):
        result = generate_caption(MagicMock(), "test_image.jpg", 50)
    assert result[0] == "test_image.jpg"
    assert "Unexpected error: Test error" in result[1]

def test_output_caption(capsys):
    with patch('imgcap.console.print') as mock_print:
        output_caption("test_image.jpg", "A test caption", "json", True, True)
    mock_print.assert_called_once_with('[{"path": "test_image.jpg", "caption": "A test caption"}]')

@patch('imgcap.pipeline')
@patch('imgcap.Image.open')
def test_cli(mock_image_open, mock_pipeline, tmp_path):
    mock_pipeline.return_value = MagicMock(return_value=[{"generated_text": "A test caption"}])
    
    # Create a test image file
    test_image = tmp_path / "test_image.jpg"
    test_image.touch()
    
    runner = CliRunner()
    with patch('imgcap.console.print') as mock_print:
        result = runner.invoke(cli, [str(test_image), '--output', 'json'])
    
    assert result.exit_code == 0
    mock_print.assert_has_calls([
        call('[{"path": "' + str(test_image) + '", "caption": "A test caption"}]'),
        call('\n[bold green]Processed 1 images successfully![/bold green]')
    ], any_order=True)

@patch('imgcap.pipeline')
def test_cli_recursive(mock_pipeline, tmp_path):
   
    (tmp_path / "subdir").mkdir()
    (tmp_path / "test1.jpg").touch()
    (tmp_path / "subdir" / "test2.jpg").touch()
    
    mock_pipeline.return_value = MagicMock(return_value=[{"generated_text": "A test caption"}])
    
    runner = CliRunner()
    with patch('imgcap.console.print') as mock_print:
        result = runner.invoke(cli, [str(tmp_path), '--recursive', '--output', 'json'])
    
    assert result.exit_code == 0
    assert mock_print.call_count == 3  
    mock_print.assert_any_call('\n[bold green]Processed 2 images successfully![/bold green]') 

if __name__ == '__main__':
    pytest.main()
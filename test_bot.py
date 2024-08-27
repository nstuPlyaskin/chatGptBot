import pytest
from unittest.mock import AsyncMock, patch
from main import start, handle_message

# test username answer
@pytest.mark.asyncio
@patch('main.AsyncOpenAI')
@patch('telegram.Update')
@patch('telegram.ext.CallbackContext')
async def test_start_command(MockCallbackContext, MockUpdate, MockAsyncOpenAI):
    mock_update = MockUpdate()
    mock_context = MockCallbackContext()

    mock_update.message.from_user.first_name = 'John'
    mock_update.message.reply_text = AsyncMock()

    await start(mock_update, mock_context)

    mock_update.message.reply_text.assert_called_once_with(
        "Здравствуйте, John! Введите URL адрес вебсайта для анализа его содержимого."
    )



# test for too long msg
@pytest.mark.asyncio
@patch('main.AsyncOpenAI')
@patch('telegram.Update')
@patch('telegram.ext.CallbackContext')
async def test_handle_message_long_text(MockCallbackContext, MockUpdate, MockAsyncOpenAI):

    mock_update = MockUpdate()
    mock_context = MockCallbackContext()

    long_text = "A" * 50000
    mock_update.message.text = long_text
    mock_update.message.reply_text = AsyncMock()
    mock_update.message.chat.send_action = AsyncMock()

    mock_openai_client = MockAsyncOpenAI.return_value
    mock_openai_client.chat.completions.create = AsyncMock(return_value=AsyncMock(
        choices=[AsyncMock(
            message=AsyncMock(content='Processed long text')
        )]
    ))

    await handle_message(mock_update, mock_context)

    mock_update.message.chat.send_action.assert_called_once_with('typing')
    mock_update.message.reply_text.assert_called_once_with('Processed long text')


# test for msg with url
@pytest.mark.asyncio
@patch('main.AsyncOpenAI')
@patch('telegram.Update')
@patch('telegram.ext.CallbackContext')
async def test_handle_message_with_url(MockCallbackContext, MockUpdate, MockAsyncOpenAI):

    mock_update = MockUpdate()
    mock_context = MockCallbackContext()

    mock_update.message.text = 'http://example.com'
    mock_update.message.chat.send_action = AsyncMock()
    mock_update.message.reply_text = AsyncMock()
    
    mock_openai_client = MockAsyncOpenAI.return_value
    mock_openai_client.chat.completions.create = AsyncMock(return_value=AsyncMock(
        choices=[AsyncMock(
            message=AsyncMock(content='Industry: Tech')
        )]
    ))

    await handle_message(mock_update, mock_context)

    mock_update.message.chat.send_action.assert_called_once_with('typing')
    mock_update.message.reply_text.assert_called_once_with('Industry: Tech')

# test for msg without url
@pytest.mark.asyncio
@patch('main.AsyncOpenAI')
@patch('telegram.Update')
@patch('telegram.ext.CallbackContext')
async def test_handle_message_without_url(MockCallbackContext, MockUpdate, MockAsyncOpenAI):

    mock_update = MockUpdate()
    mock_context = MockCallbackContext()

    mock_update.message.text = 'Hello'
    mock_update.message.reply_text = AsyncMock()
    mock_update.message.chat.send_action = AsyncMock()

    mock_openai_client = MockAsyncOpenAI.return_value
    mock_openai_client.chat.completions.create = AsyncMock(return_value=AsyncMock(
        choices=[AsyncMock(
            message=AsyncMock(content='Ошибка: вы ввели не URL, введите заново.')
        )]
    ))

    await handle_message(mock_update, mock_context)

    # Проверка вызова send_action и reply_text с ожидаемым сообщением
    mock_update.message.chat.send_action.assert_called_once_with('typing')
    mock_update.message.reply_text.assert_called_once_with('Ошибка: вы ввели не URL, введите заново.')

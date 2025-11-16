"""
End-to-end test script for AI Video Editor.
Tests the complete workflow: Upload -> Chat -> Export
"""

import requests
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")


def test_health_check():
    """Test 1: Health check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    try:
        response = requests.get(f"{API_URL}/health")
        response.raise_for_status()
        data = response.json()

        print_info(f"Status: {data['status']}")
        print_info(f"Version: {data['version']}")
        print_success("Health check passed")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_video_upload(video_path: str = None):
    """Test 2: Video upload"""
    print("\n" + "="*60)
    print("TEST 2: Video Upload")
    print("="*60)

    if not video_path:
        print_warning("No video file provided. Skipping upload test.")
        print_info("To test upload, provide a video path: python test_workflow.py /path/to/video.mp4")
        return None

    video_file = Path(video_path)
    if not video_file.exists():
        print_error(f"Video file not found: {video_path}")
        return None

    print_info(f"Uploading: {video_file.name}")

    try:
        with open(video_file, 'rb') as f:
            files = {'file': (video_file.name, f, 'video/mp4')}
            response = requests.post(f"{API_URL}/upload", files=files)
            response.raise_for_status()

        data = response.json()
        session_id = data['session_id']

        print_success(f"Video uploaded successfully")
        print_info(f"Session ID: {session_id}")
        print_info(f"Duration: {data['metadata']['duration']:.2f}s")
        print_info(f"Resolution: {data['metadata']['width']}x{data['metadata']['height']}")
        print_info(f"FPS: {data['metadata']['fps']:.2f}")

        return session_id
    except Exception as e:
        print_error(f"Upload failed: {e}")
        return None


def test_chat_subtitle_addition(session_id: str):
    """Test 3: Add subtitles via chat"""
    print("\n" + "="*60)
    print("TEST 3: Add Subtitles via Chat")
    print("="*60)

    if not session_id:
        print_warning("No session ID. Skipping chat test.")
        return False

    # Test messages
    test_messages = [
        "Add subtitle 'Hello World!' from 0 to 3 seconds with red color",
        "Add subtitle 'Welcome to AI Video Editor' from 3 to 7 seconds, size 48, bold",
        "Add 'This is a test' from 7 to 10 seconds with yellow color and Arial font",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{BLUE}Message {i}:{RESET} {message}")

        try:
            response = requests.post(
                f"{API_URL}/chat",
                json={
                    "session_id": session_id,
                    "message": message
                }
            )
            response.raise_for_status()
            data = response.json()

            ai_response = data['message']['content']
            subtitle_count = len(data['subtitles'])

            print_success(f"AI Response: {ai_response}")
            print_info(f"Total subtitles: {subtitle_count}")

            time.sleep(1)  # Small delay between requests

        except Exception as e:
            print_error(f"Chat request failed: {e}")
            return False

    print_success("All chat messages processed successfully")
    return True


def test_get_subtitles(session_id: str):
    """Test 4: Get subtitles"""
    print("\n" + "="*60)
    print("TEST 4: Get Subtitles")
    print("="*60)

    if not session_id:
        print_warning("No session ID. Skipping.")
        return False

    try:
        response = requests.get(f"{API_URL}/subtitles/{session_id}")
        response.raise_for_status()
        subtitles = response.json()

        print_success(f"Retrieved {len(subtitles)} subtitles")

        for i, sub in enumerate(subtitles, 1):
            print(f"\n  Subtitle {i}:")
            print(f"    Text: {sub['text']}")
            print(f"    Time: {sub['start_time']:.1f}s - {sub['end_time']:.1f}s")
            print(f"    Style: {sub['style']['font_color']}, "
                  f"size {sub['style']['font_size']}, "
                  f"font {sub['style']['font_family']}")

        return True
    except Exception as e:
        print_error(f"Failed to get subtitles: {e}")
        return False


def test_export_video(session_id: str):
    """Test 5: Export video"""
    print("\n" + "="*60)
    print("TEST 5: Export Video")
    print("="*60)

    if not session_id:
        print_warning("No session ID. Skipping export test.")
        return False

    try:
        print_info("Exporting video with burned subtitles...")
        print_warning("This may take a while depending on video length...")

        response = requests.post(
            f"{API_URL}/export",
            json={
                "session_id": session_id,
                "filename": "test_output.mp4"
            }
        )
        response.raise_for_status()
        data = response.json()

        download_url = f"{BASE_URL}{data['download_url']}"

        print_success(f"Video exported successfully")
        print_info(f"Filename: {data['filename']}")
        print_info(f"Download URL: {download_url}")

        return True
    except Exception as e:
        print_error(f"Export failed: {e}")
        if hasattr(e, 'response') and e.response:
            print_error(f"Details: {e.response.text}")
        return False


def test_chat_history(session_id: str):
    """Test 6: Get chat history"""
    print("\n" + "="*60)
    print("TEST 6: Chat History")
    print("="*60)

    if not session_id:
        print_warning("No session ID. Skipping.")
        return False

    try:
        response = requests.get(f"{API_URL}/chat/history/{session_id}")
        response.raise_for_status()
        data = response.json()

        message_count = data['count']
        print_success(f"Retrieved {message_count} chat messages")

        for i, msg in enumerate(data['messages'][:5], 1):  # Show first 5
            print(f"\n  Message {i} ({msg['type']}):")
            print(f"    {msg['content'][:100]}...")

        return True
    except Exception as e:
        print_error(f"Failed to get chat history: {e}")
        return False


def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}")
    print("AI VIDEO EDITOR - END-TO-END TEST")
    print(f"{'='*60}{RESET}\n")

    # Check if video path provided
    video_path = sys.argv[1] if len(sys.argv) > 1 else None

    results = {
        "Health Check": False,
        "Video Upload": False,
        "Chat Subtitle Addition": False,
        "Get Subtitles": False,
        "Export Video": False,
        "Chat History": False,
    }

    # Test 1: Health check
    results["Health Check"] = test_health_check()

    if not results["Health Check"]:
        print_error("\nServer is not running or health check failed!")
        print_info("Please start the server: uvicorn app.main:app --reload")
        return

    # Test 2: Upload video
    session_id = test_video_upload(video_path)
    results["Video Upload"] = session_id is not None

    if not session_id:
        print_warning("\nSkipping remaining tests (no video uploaded)")
        print_summary(results)
        return

    # Test 3: Chat
    results["Chat Subtitle Addition"] = test_chat_subtitle_addition(session_id)

    # Test 4: Get subtitles
    results["Get Subtitles"] = test_get_subtitles(session_id)

    # Test 5: Export
    results["Export Video"] = test_export_video(session_id)

    # Test 6: Chat history
    results["Chat History"] = test_chat_history(session_id)

    # Summary
    print_summary(results)


def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60 + "\n")

    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{test_name:.<40} {status}")

    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60 + "\n")

    if passed == total:
        print_success("All tests passed! 🎉")
    elif passed > 0:
        print_warning(f"Some tests passed ({passed}/{total})")
    else:
        print_error("All tests failed")


if __name__ == "__main__":
    main()

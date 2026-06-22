import time
import threading
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import DemoModel
from .signals import (
    sync_async_signal,
    thread_check_signal,
    transaction_check_signal,
    execution_logs,
    log_message
)
from .utils import Rectangle

def dashboard_view(request):
    """
    Renders the frontend dashboard for running and visualizing the demonstrations.
    """
    return render(request, 'signals_demo/dashboard.html')

@csrf_exempt
@require_POST
def test_sync_async(request):
    """
    Triggers the synchronous vs asynchronous check.
    Blocks the signal handler with time.sleep(2) to demonstrate synchronous execution.
    """
    execution_logs.clear()
    
    start_time = time.time()
    log_message(f"[Caller] Starting execution. Time: {time.strftime('%H:%M:%S')}")
    
    log_message("[Caller] Sending sync_async_signal...")
    sync_async_signal.send(sender=None)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    log_message(f"[Caller] Returned back to caller. Time: {time.strftime('%H:%M:%S')}")
    log_message(f"[Caller] Total execution time: {elapsed:.4f} seconds.")
    
    # Since sleep is 2 seconds, elapsed must be > 2 seconds
    proven = elapsed >= 2.0
    
    return JsonResponse({
        "success": True,
        "logs": list(execution_logs),
        "elapsed": round(elapsed, 4),
        "proven": proven,
        "explanation": "Because the execution blocked inside the receiver for 2 seconds before returning control to the caller, the caller printed 'Returned back to caller' ONLY after the receiver finished. This proves Django signals are executed synchronously by default."
    })

@csrf_exempt
@require_POST
def test_thread_check(request):
    """
    Triggers the thread check.
    Compares the Caller's Thread ID/Name and Receiver's Thread ID/Name.
    """
    execution_logs.clear()
    
    caller_thread_id = threading.get_ident()
    caller_thread_name = threading.current_thread().name
    
    log_message(f"[Caller] Caller Thread ID: {caller_thread_id}, Name: '{caller_thread_name}'")
    log_message("[Caller] Sending thread_check_signal...")
    
    responses = thread_check_signal.send(sender=None)
    
    receiver_info = responses[0][1] if responses else None
    
    same_thread = False
    rec_id = None
    rec_name = "Unknown"
    
    if receiver_info:
        rec_id = receiver_info["thread_id"]
        rec_name = receiver_info["thread_name"]
        same_thread = (caller_thread_id == rec_id)
        log_message(f"[Caller] Comparison: Caller Thread ({caller_thread_id}) {'==' if same_thread else '!='} Receiver Thread ({rec_id})")
    
    return JsonResponse({
        "success": True,
        "logs": list(execution_logs),
        "caller_thread": f"Thread '{caller_thread_name}' (ID: {caller_thread_id})",
        "receiver_thread": f"Thread '{rec_name}' (ID: {rec_id})" if receiver_info else "N/A",
        "proven": same_thread,
        "explanation": "The Thread ID and Name are identical in both the caller and receiver, proving that Django signals run in the same thread as the caller."
    })

@csrf_exempt
@require_POST
def test_transaction_check(request):
    """
    Triggers the transaction check.
    Saves a record, triggers the signal, inserts another record inside receiver,
    forces rollback, and verifies if the receiver record is rolled back.
    """
    execution_logs.clear()
    
    # Clear any previous records
    DemoModel.objects.all().delete()
    
    log_message(f"[Caller] Initial DB Record Count: {DemoModel.objects.count()}")
    
    rollback_occurred = False
    try:
        with transaction.atomic():
            log_message("[Caller] Opened transaction.atomic() block.")
            
            # Create a record in caller
            log_message("[Caller] Creating record 'Caller Record'...")
            DemoModel.objects.create(name="Caller Record")
            
            log_message(f"[Caller] Count in DB (before signal): {DemoModel.objects.count()}")
            
            # Send signal
            log_message("[Caller] Sending transaction_check_signal...")
            transaction_check_signal.send(sender=None)
            
            # Count after signal receiver ran
            current_count = DemoModel.objects.count()
            log_message(f"[Caller] Count in DB (after signal): {current_count}")
            
            log_message("[Caller] Raising ValueError to trigger transaction rollback...")
            raise ValueError("Simulated Rollback Exception")
            
    except ValueError as e:
        rollback_occurred = True
        log_message(f"[Caller] Caught expected rollback exception: {e}")
        
    final_count = DemoModel.objects.count()
    log_message(f"[Caller] Post-transaction DB Record Count: {final_count}")
    
    # If the receiver runs in the same transaction, its record is rolled back, leaving count as 0.
    proven = (final_count == 0 and rollback_occurred)
    
    return JsonResponse({
        "success": True,
        "logs": list(execution_logs),
        "proven": proven,
        "explanation": "Inside the transaction block, the receiver successfully queried the database and saw the caller's pending record, then inserted its own. When the transaction was aborted, BOTH records were completely rolled back, resulting in a database count of 0. This proves that Django signals execute within the same database transaction as the caller."
    })

@csrf_exempt
@require_POST
def test_rectangle(request):
    """
    Instantiates the Rectangle class with length and width,
    iterates over it to collect output, and returns it.
    """
    length_str = request.POST.get("length")
    width_str = request.POST.get("width")
    
    try:
        length = int(length_str)
        width = int(width_str)
    except (ValueError, TypeError):
        return JsonResponse({
            "success": False,
            "error": "Length and width must be valid integers."
        })
        
    try:
        rect = Rectangle(length, width)
        yielded_items = list(rect)
        
        return JsonResponse({
            "success": True,
            "yielded_items": yielded_items,
            "explanation": f"Successfully iterated over Rectangle instance: yielded {yielded_items[0]} followed by {yielded_items[1]}."
        })
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        })

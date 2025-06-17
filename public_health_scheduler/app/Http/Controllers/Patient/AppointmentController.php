<?php

namespace App\Http\Controllers\Patient;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Appointment;
use App\Models\HealthCenter;
use App\Models\Service;
use Illuminate\Support\Facades\Auth;
use Carbon\Carbon;
use Illuminate\Support\Str; // Added for Str::title

class AppointmentController extends Controller
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        $appointments = Appointment::with(['healthCenter', 'service'])
            ->where('user_id', Auth::id())
            ->orderBy('scheduled_time', 'desc')
            ->paginate(10);
        return view('patient.appointments.index', compact('appointments'));
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        $healthCenters = HealthCenter::orderBy('name')->get();
        $services = Service::orderBy('name')->get();
        return view('patient.appointments.create', compact('healthCenters', 'services'));
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        $request->validate([
            'health_center_id' => 'required|exists:health_centers,id',
            'service_id' => 'required|exists:services,id',
            'scheduled_time' => 'required|date|after_or_equal:now',
            // 'doctor_id' => 'nullable|exists:users,id', // Example for future use
        ]);

        $healthCenter = HealthCenter::find($request->health_center_id);
        $scheduledTime = Carbon::parse($request->scheduled_time);

        // 1. Check against Health Center Operating Hours
        if ($healthCenter && $healthCenter->operating_hours) {
            $dayOfWeek = strtolower($scheduledTime->format('l')); // 'monday', 'tuesday', etc.
            $time = $scheduledTime->format('H:i');

            if (!isset($healthCenter->operating_hours[$dayOfWeek])) {
                return back()->withErrors(['scheduled_time' => 'The health center is closed on ' . Str::title($dayOfWeek) . '.'])->withInput();
            }

            $hours = $healthCenter->operating_hours[$dayOfWeek];
            if (isset($hours['is_closed']) && $hours['is_closed'] === true) {
                 return back()->withErrors(['scheduled_time' => 'The health center is closed on ' . Str::title($dayOfWeek) . '.'])->withInput();
            }

            // Ensure 'open' and 'close' keys exist and are not empty before comparison
            if (empty($hours['open']) || empty($hours['close'])) {
                return back()->withErrors(['scheduled_time' => 'Operating hours (open/close times) for ' . Str::title($dayOfWeek) . ' are missing or not properly configured for this center.'])->withInput();
            }

            if ($time < $hours['open'] || $time >= $hours['close']) {
                return back()->withErrors(['scheduled_time' => 'The selected time is outside the health center\'s operating hours (' . $hours['open'] . ' - ' . $hours['close'] . ' on ' . Str::title($dayOfWeek) . ').'])->withInput();
            }
        }
        // If operating_hours is null or day not defined, booking is allowed (or add specific error handling)

        Appointment::create([
            'user_id' => Auth::id(),
            'health_center_id' => $request->health_center_id,
            'service_id' => $request->service_id,
            'scheduled_time' => $scheduledTime,
            // 'doctor_id' => $request->doctor_id,
            'status' => 'pending',
        ]);

        return redirect()->route('patient.appointments.index')->with('success', 'Appointment scheduled successfully. It is currently pending confirmation.');
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}

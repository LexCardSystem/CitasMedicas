<x-app-layout> {{-- Use your main app layout --}}
    <h2>Dashboard</h2>
    <p>You're logged in!</p>
<p><a href="{{ route('patient.appointments.create') }}">Schedule New Appointment</a></p>
</x-app-layout>

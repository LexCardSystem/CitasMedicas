<x-app-layout>
    <x-slot name="header">
        <h2 class="font-semibold text-xl text-gray-800 leading-tight">
            {{ __('Schedule New Appointment') }}
        </h2>
    </x-slot>

    <div class="py-12">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 bg-white border-b border-gray-200">
                    <form method="POST" action="{{ route('patient.appointments.store') }}">
                        @csrf

                        <!-- Health Center -->
                        <div class="mt-4">
                            <label for="health_center_id">Health Center</label>
                            <select id="health_center_id" name="health_center_id" class="block mt-1 w-full" required>
                                <option value="">Select a Health Center</option>
                                @foreach ($healthCenters ?? [] as $center)
                                    <option value="{{ $center->id }}" {{ old('health_center_id') == $center->id ? 'selected' : '' }}>
                                        {{ $center->name }}
                                    </option>
                                @endforeach
                            </select>
                        </div>

                        <!-- Service -->
                        <div class="mt-4">
                            <label for="service_id">Service</label>
                            <select id="service_id" name="service_id" class="block mt-1 w-full" required>
                                <option value="">Select a Service</option>
                                @foreach ($services ?? [] as $service)
                                    <option value="{{ $service->id }}" {{ old('service_id') == $service->id ? 'selected' : '' }}>
                                        {{ $service->name }} ({{ $service->type }})
                                    </option>
                                @endforeach
                            </select>
                        </div>

                        <!-- Scheduled Time -->
                        <div class="mt-4">
                            <label for="scheduled_time">Preferred Date and Time</label>
                            <input type="datetime-local" id="scheduled_time" name="scheduled_time" class="block mt-1 w-full" value="{{ old('scheduled_time') }}" required>
                        </div>

                        <!-- Doctor (Optional for now, will be part of advanced scheduling) -->
                        {{--
                        <div class="mt-4">
                            <label for="doctor_id">Preferred Doctor (Optional)</label>
                            <select id="doctor_id" name="doctor_id" class="block mt-1 w-full">
                                <option value="">Any Available Doctor</option>
                                {{-- @foreach ($doctors ?? [] as $doctor)
                                    <option value="{{ $doctor->id }}">{{ $doctor->name }}</option>
                                @endforeach --}}
                            </select>
                        </div>
                        --}}

                        <div class="flex items-center justify-end mt-4">
                            <button type="submit" class="ml-4">
                                {{ __('Schedule Appointment') }}
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>

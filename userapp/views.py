from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from adminapp.models import *
from datetime import date
import urllib.request
import urllib.parse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import random
import requests
# Create your views here.






def index(request):
    return render(request,"index.html")

def elections(request):
    # Get all elections from today onwards
    future_elections = ElectionModel.objects.filter(election_date__gte=date.today()).order_by('election_date')
    today = date.today()
    return render(request, "elections.html", {'elections': future_elections, 'today': today})


def candidates(request, id):
    election = get_object_or_404(ElectionModel, pk=id)
    request.session["id_of_election"] = election.pk
    print(election,"uytdvguxesgfuyskgfkysyg")
    candidates = election.election_candidates.all()
    return render(request, "candidates.html", {'candidates': candidates, 'election': election})


def results(request):
    return render(request,"results.html")


# def voting_page(request,id):
#     candidate = CandidateModel.objects.get(pk=id)
#     election_obj = ElectionModel.objects.get(pk=candidate.election.id)
#     # request.session['current_election'] = election_obj.id

#     if request.method == 'POST':
#         phone = request.POST.get('phone')
#         aadhar = request.POST.get('aadhar')
#         request.session['aadhar_number'] = aadhar
#         otp = str(random.randint(1111, 9999))

#         voter, created = VoterModel.objects.get_or_create(aadhar=aadhar)
#         if not created:
#             if voter.phone != phone:
#                 messages.error(request, 'Please Enter Valid Mobile Number Associated with this Aadhar Number')
#                 return redirect('candidates',id=election_obj.pk)

#         voter.phone = phone
#         voter.otp = otp
#         print(otp,"otp")
#         voter.save()
#         if voter in election_obj.voters.all():
#             messages.error(request, "you have already submited your vote")
#             return redirect('candidates',id=election_obj.pk)

#         resp = sendSMS(voter.aadhar, otp, voter.phone)
#         messages.success(request, 'Otp has been sent to your registered Mobile Number')
#         return redirect('voter_otp',id=voter.pk,cand_id=id)
#     return render(request, 'voting-page.html')



from django.core.mail import send_mail
from django.conf import settings
import random
import os
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import render, redirect
import face_recognition

from adminapp.models import Voter, CandidateModel, ElectionModel, VoterModel
from blockchain_utils import store_hash_on_blockchain

def voting_page(request, id):
    candidate = CandidateModel.objects.get(pk=id)
    election_obj = ElectionModel.objects.get(pk=candidate.election.id)

    if request.method == 'POST':
        aadhar = request.POST.get('aadhar')
        email = request.POST.get('email')
        request.session['aadhar_number'] = aadhar

        # Generate OTP
        otp = str(random.randint(1111, 9999))

        voter, created = VoterModel.objects.get_or_create(aadhar=aadhar)
        if not created:
            if voter.email != email:
                messages.error(request, 'Please Enter Valid Email Associated with this Voter Number')
                return redirect('candidates', id=election_obj.pk)

        voter.email = email  # Update voter's email
        voter.otp = otp
        print(otp, "otp")
        voter.save()

        if voter in election_obj.voters.all():
            messages.error(request, "You have already submitted your vote")
            return redirect('candidates', id=election_obj.pk)

        # Send OTP via email
        subject = 'OTP Verification for Voting'
        otp_message = f'Your OTP for verification is: {voter.otp}'
        message = f'Hello,\n\nYou are attempting to cast a vote. {otp_message}\n\nIf you did not request this OTP, please ignore this message.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [voter.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        messages.success(request, 'OTP has been sent to your registered Email')
        return redirect('voter_otp', id=voter.pk, cand_id=id)

    return render(request, 'voting-page.html')


def voter_otp(request, id, cand_id):
    voter = VoterModel.objects.get(pk=id)
    if request.method == 'POST':
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        otp = otp1 + otp2 + otp3 + otp4
        print(voter.otp, 'org otp')
        print(otp, 'entered otp')

        if otp == voter.otp:
            voter.status = 'Verified'
            voter.otp = None
            voter.save()
            messages.success(request, 'OTP verification successful')
            aadhar_number = request.session.get('aadhar_number')
            request.session['aadhar_number_in_otp_page'] = aadhar_number
            return redirect('fingerprint', id, cand_id)
        else:
            messages.error(request, 'Incorrect OTP')
            return redirect('voter_otp', id, cand_id)

    return render(request, 'voter-otp.html')


# Face Verification Function
def compare_faces(known_face_path, unknown_face_path):
    known_image = face_recognition.load_image_file(known_face_path)
    unknown_image = face_recognition.load_image_file(unknown_face_path)

    known_face_encodings = face_recognition.face_encodings(known_image)
    unknown_face_encodings = face_recognition.face_encodings(unknown_image)

    if len(known_face_encodings) != 1 or len(unknown_face_encodings) != 1:
        return False

    results = face_recognition.compare_faces([known_face_encodings[0]], unknown_face_encodings[0])
    return results[0]


# Face Verification (Kept as "fingerprint" to maintain existing function name)
def fingerprint(request, id, cand_id):
    if request.method == 'POST':
        aadhar_number = request.session.get('aadhar_number_in_otp_page')
        try:
            voter = Voter.objects.get(aadhaar_number=aadhar_number)
        except Voter.DoesNotExist:
            messages.error(request, "No voter found with this Voter number.")
            return render(request, 'fingerprint.html')

        image_data = request.POST.get('imageData')
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        temp_path = default_storage.save('temp/' + 'temp.' + ext, data)

        election_id = request.session.get('id_of_election')
        election = ElectionModel.objects.get(pk=election_id)

        # Compare the real-time captured image with stored image
        if compare_faces(default_storage.path(temp_path), voter.image.path):
            messages.success(request, "Face matched successfully.")
            election.successful_votes += 1
            election.save()
            return redirect('cast_vote', id=id, cand_id=cand_id)
        else:
            messages.error(request, "Face does not match.")
            election.unsuccessful_votes += 1
            election.save()
        return redirect('fingerprint', id, cand_id)
    
    return render(request, 'fingerprint.html')

import base64



def cast_vote(request, id, cand_id):
    voter = VoterModel.objects.get(pk=id)
    candidate = CandidateModel.objects.get(pk=cand_id)
    election_obj = ElectionModel.objects.get(pk=candidate.election.id)

    if voter not in election_obj.voters.all():
        election_obj.voters.add(voter)
        candidate.voters.add(voter)
        candidate.votes += 1
        candidate.save()
        data = f"{voter.id}{candidate.id}{election_obj.id}"
        store_hash_on_blockchain(data)
        messages.success(request, 'Vote submitted successfully')
        return redirect('elections')
    else:
        messages.error(request, "You have already submitted your vote")
        return redirect('candidates', id=election_obj.id)


def voter_results(request):
    elections = ElectionModel.objects.filter(election_date__lt = date.today())
    return render(request, 'voter-results.html',{'elections':elections})





def voter_verify_results(request, id):
    election = ElectionModel.objects.get(pk=id)
    votes = VotesModel.objects.filter(election=election)
    total_votes = votes.count()
    candidates = CandidateModel.objects.filter(election=election)
    winner = candidates.order_by('-votes').first()
    has_votes = votes.exists()
    
    return render(request, 'voter-result-details.html', {
        'candidates': candidates,
        'total_votes': total_votes,
        'votes': votes,
        'winner': winner,
        'has_votes': has_votes
    })



def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            messages.success(request, 'Login Successful')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid Login Credentials')
            return redirect('admin_login')
    return render(request,"admin-login.html")

def sendSMS(user,otp,mobile):
    data =  urllib.parse.urlencode({'username':'invoice','apikey': '' , 'mobile': mobile,
        'message' : f'Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.vvit.in server. Thank you', 'senderid': 'co'})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://smslogin.co/v3/api.php?")
    f = urllib.request.urlopen(request, data)
    return f.read()

# views.py
from django.shortcuts import render, redirect
from .models import Contact

def contact(request):
    if request.method == 'POST':
        # Get data from the POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        project = request.POST.get('project')
        message = request.POST.get('message')
        print(name, email, project, message)
        # Save the data into the Contact model
        contact = Contact(name=name, email=email, project=project, message=message)
        contact.save()
        messages.success(request, 'Thank You')

        return redirect('contact') 

    return render(request, 'contact.html')




from django.shortcuts import render
import joblib
import numpy as np

def predict_election(request):
    result = None
    if request.method == 'POST':
        # Load the model
        model = joblib.load('voting.pkl')
        
        # Get input values from the form
        party = int(request.POST['party'])
        gender = int(request.POST['gender'])
        criminal_cases = int(request.POST['criminal_cases'])
        age = float(request.POST['age'])
        category = int(request.POST['category'])
        education = int(request.POST['education'])
        total_votes = int(request.POST['total_votes'])
        total_electors = int(request.POST['total_electors'])
        assets = float(request.POST['assets'])
        liabilities = float(request.POST['liabilities'])
        
        # Make prediction
        features = np.array([[party, gender, criminal_cases, age, category, education, total_votes, total_electors, assets, liabilities]])
        prediction = model.predict(features)
        
        result = "Winner" if prediction[0] == 1 else "Not a Winner"
    
    return render(request, 'form.html', {'result': result})

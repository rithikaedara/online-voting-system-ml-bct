from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from blockchain_utils import store_hash_on_blockchain
import base64

# views.py
from django.shortcuts import render
from userapp.models import Contact

def admin_dashboard(request):
    elections = ElectionModel.objects.all().count()
    candidates = CandidateModel.objects.all().count()
    votes = VotesModel.objects.all().count()
    contact_info = Contact.objects.all()  
    
    return render(request, 'admin/admin-dashboard.html', {
        'elections': elections,
        'candidates': candidates,
        'votes': votes,
        'contact_info': contact_info  
    })


def admin_add_election(request):
    if request.method == 'POST':
        election_name = request.POST.get('electionname')
        head_of_election = request.POST.get('headofelection')
        election_picture = request.FILES['electionpicture']
        election_date = request.POST.get('electiondate')
        constituency = request.POST.get('constituency')
        area = request.POST.get('electionarea')
        address = request.POST.get('electionaddress')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip = request.POST.get('zip')
        ElectionModel.objects.create(
            election_name=election_name, election_head=head_of_election,
            election_date=election_date, election_picture=election_picture,
            constituency=constituency, area=area, address=address,
            state=state, city=city, zip=zip
        )
        data = f"{election_name}{head_of_election}{election_date}{constituency}{area}{address}{city}{state}{zip}"
        store_hash_on_blockchain(data)
        messages.success(request, 'Election has been added successfully')
        return redirect('admin_add_election')
    return render(request, 'admin/admin-addelection.html')

def admin_add_candidates(request):
    elections = ElectionModel.objects.all()
    if request.method == 'POST':
        candidate_name = request.POST.get('candidatename')
        party_name = request.POST.get('partyname')
        election_id = request.POST.get('electionname')
        symbol = request.FILES['symbol']
        election = ElectionModel.objects.get(pk=election_id)
        CandidateModel.objects.create(
            election=election, candidate_name=candidate_name,
            party_name=party_name, symbol=symbol
        )
        election.candidates_count += 1
        election.save()
        data = f"{candidate_name}{party_name}{election_id}"
        store_hash_on_blockchain(data)
        messages.success(request, 'Candidate added successfully')
        return redirect('admin_add_candidates')
    return render(request, 'admin/admin-addcandidates.html', {
        'elections': elections
    })


def admin_view_elections(request):
    elections = ElectionModel.objects.all()

    return render(request, 'admin/admin-view-elections.html',{
        'elections':elections
    })

def admin_view_candidates(request,id):
    election = ElectionModel.objects.get(pk=id)
    candidates = election.election_candidates.all()
    return render(request, 'admin/admin-view-candidates.html',{
        'candidates':candidates,
        'election':election
    })

def admin_results(request):
    elections = ElectionModel.objects.all()
    return render(request, 'admin/admin-results.html',{
        'elections':elections
    })

def verify_results(request, id):
    election = ElectionModel.objects.get(pk=id)
    candidates = CandidateModel.objects.filter(election=election)

    successful_votes = election.successful_votes
    unsuccessful_votes = election.unsuccessful_votes
    total_votes = successful_votes + unsuccessful_votes

    return render(request, 'admin/admin-result-details.html', {
        'candidates': candidates,
        'successful_votes': successful_votes,
        'unsuccessful_votes': unsuccessful_votes,
        'total_votes': total_votes,
    })
import os
import base64
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Voter

def add_voters(request):
    if request.method == 'POST':
        aadhaar_number = request.POST.get('aadhaarNumber')
        image_data = request.POST.get('imageData')

        

        if Voter.objects.filter(aadhaar_number=aadhaar_number).exists():
            messages.error(request, f'A voter with Voter number {aadhaar_number} already exists.')
            return redirect('add_voters')

        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        image_path = default_storage.save(f'user_images/{aadhaar_number}.{ext}', data)

        voter = Voter(aadhaar_number=aadhaar_number, image=image_path)
        voter.save()

        store_hash_on_blockchain(aadhaar_number)

        messages.success(request, 'Voter has been successfully added.')
        return redirect('add_voters')

    return render(request, "admin/add-voters.html")



def manage_voters(request):
    voters = Voter.objects.all()
    return render(request, "admin/manage-voters.html", {'voters': voters})

def remove_voter(request, voter_id):
    Voter.objects.filter(id=voter_id).delete()
    return redirect('manage_voters')





import os
import pandas as pd
from django.shortcuts import render, redirect
from django.core.files import File
from django.conf import settings
from .models import Voter
from .forms import CSVUploadForm

def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():
                aadhaar_number = str(row["aadhaar_number"]).strip()
                image_path = str(row["image_path"]).strip()

                full_image_path = os.path.join(settings.BASE_DIR, image_path)

                if os.path.exists(full_image_path):
                    with open(full_image_path, "rb") as img_file:
                        voter, created = Voter.objects.get_or_create(aadhaar_number=aadhaar_number)
                        voter.image.save(os.path.basename(image_path), File(img_file), save=True)

            return redirect("upload_csv")  # Redirect to a success page

    else:
        form = CSVUploadForm()
    
    return render(request, "admin/upload_csv.html", {"form": form})

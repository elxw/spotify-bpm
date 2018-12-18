from django.shortcuts import render, redirect, reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse

import sys
import os
import spotipy
import spotipy.util as util
import urllib.request
import requests


from .models import Playlist, Track


username = ""
sp = None

def home(request):
  return render(request, 'home.html', {})

def getPlaylist(request):
  global username
  global sp
  if 'username' not in request.session:
    return redirect(reverse('home'))
  
  username = request.session['username']
  request.session['username'] = username
  scope = 'playlist-read-private'
  token = util.prompt_for_user_token(username, scope, os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'],redirect_uri='http://127.0.0.1:8000/')
  sp = spotipy.Spotify(auth=token)
  # playlist_name = request.POST['playlist_name']
  playlists = []
  results = sp.current_user_playlists(limit=50, offset=0)
  for item in results['items']:
    if (Playlist.objects.filter(playlistId=item['id']).count() == 0):
      p = Playlist(name=item['name'], imageUrl=item['images'][0]['url'], playlistId=item['id'])
      p.save()
    else:
      p = Playlist.objects.get(playlistId=item['id'])
    playlists.append(p)
  return render(request, 'playlists.html', {'playlists': playlists})

def show_tracks(request, tracks, playlistId):
  filteredTracks = []
  playlist = Playlist.objects.get(playlistId=playlistId)
  for i, item in enumerate(tracks['items']):
    track = item['track']
    token = util.prompt_for_user_token(request.session['username'], 'playlist-read-private',os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'],redirect_uri='http://127.0.0.1:8000/')
    sp = spotipy.Spotify(auth=token)
    features = sp.audio_features(track['id'])
    if (Track.objects.filter(id=track['id']).count() > 0):
      t = Track.objects.get(id=track['id'])
    else:
      t = Track(id=track['id'], name=track['name'], artist=track['artists'][0]['name'], tempo=int(features[0]['tempo']))
      t.save()
    playlist.tracks.add(t)
    filteredTracks.append(t)
  return filteredTracks

def analyze(request, playlistId):
  global username
  playlist = Playlist.objects.get(playlistId=playlistId)

  if (playlist.tracks.all().count() == 0):
    print("GETTING TRACKS")
    scope = 'playlist-read-private'
    token = util.prompt_for_user_token(username, scope, client_id='3a055eafaedc49a39418e53229fd0de7', client_secret='edc65041299348c7b0920d1406ee26d2',redirect_uri='http://127.0.0.1:8000/')
    sp = spotipy.Spotify(auth=token)
    results = sp.user_playlist(username, playlistId, fields="tracks,next,tempo")
    tracks = results['tracks']
    filteredTracks = show_tracks(request, tracks, playlistId)
    while tracks['next']:
        tracks = sp.next(tracks)
        filteredTracks.extend(show_tracks(request, tracks, playlistId))
  else:
    print("tracks exist!")
    filteredTracks = [x for x in Playlist.objects.get(playlistId=playlistId).tracks.all()]

  filteredTracks.sort(key=lambda x: x.tempo)
  return render(request, 'tracks.html', {'tracks': filteredTracks, 'playlist': playlist})


def goals(request):
  return render(request, 'goals.html', {})

# python3 -m http.server
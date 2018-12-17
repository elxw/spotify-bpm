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
  if request.method == "POST":
    username = request.POST['username']
    request.session['username'] = username
    scope = 'playlist-read-private'
    token = util.prompt_for_user_token(username, scope, os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'],redirect_uri='http://127.0.0.1:8000/')
    sp = spotipy.Spotify(auth=token)
    # playlist_name = request.POST['playlist_name']
    playlists = []
    results = sp.current_user_playlists(limit=50, offset=0)
    for item in results['items']:
      p = Playlist(name=item['name'], imageUrl=item['images'][0]['url'], playlistId=item['id'])
      playlists.append(p)
  return render(request, 'playlists.html', {'playlists': playlists})

def show_tracks(request, tracks):
  filteredTracks = []
  for i, item in enumerate(tracks['items']):
    # print("=============")
    # print(item)
    track = item['track']
    
    token = util.prompt_for_user_token(request.session['username'], 'playlist-read-private',os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'],redirect_uri='http://127.0.0.1:8000/')
    sp = spotipy.Spotify(auth=token)
    features = sp.audio_features(track['id'])
    # if features[0]['tempo'] > 100 and features[0]['tempo'] < 150:
    
    if (Track.objects.filter(id=track['id']).count() > 0):
      t = Track.objects.get(id=track['id'])
    else:
      t = Track(id=track['id'], name=track['name'], artist=track['artists'][0]['name'], tempo=int(features[0]['tempo']))
      t.save()
    filteredTracks.append(t)
  return filteredTracks

def analyze(request, playlistId):
  global username
  print("analyzing %s" % playlistId)
  scope = 'playlist-read-private'
  token = util.prompt_for_user_token(username, scope, client_id='3a055eafaedc49a39418e53229fd0de7', client_secret='edc65041299348c7b0920d1406ee26d2',redirect_uri='http://127.0.0.1:8000/')
  sp = spotipy.Spotify(auth=token)
  results = sp.user_playlist(username, playlistId, fields="tracks,next,tempo")
  tracks = results['tracks']
  filteredTracks = show_tracks(request, tracks)
  while tracks['next']:
      tracks = sp.next(tracks)
      filteredTracks.extend(show_tracks(request, tracks))
  filteredTracks.sort(key=lambda x: x.tempo)
  return render(request, 'tracks.html', {'tracks': filteredTracks})


def goals(request):
  return render(request, 'goals.html', {})

# python3 -m http.server